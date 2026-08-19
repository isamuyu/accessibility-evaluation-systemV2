"""设施评价模式：打分计算 + 自动映射到Q维度（参考旧版 facilityModeMappingService）"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import (
    FacilityModeInstance, FacilityModeCheck, FacilityModeClause, FacilityModeCategory,
    FacilityEntity, FacilityCategory, FacilityScoreDetail,
    SystemScoreDetail, ControlItemCheck, StandardClause
)


def compute_actual_score(clause: FacilityModeClause, selected_option: Optional[dict]) -> tuple:
    """根据用户选择计算实际得分，返回 (actual, applicable, status)"""
    sel = selected_option or {}
    status = sel.get("status") or "pending"
    if status == "na":
        return Decimal("0"), False, "na"

    max_score = Decimal(str(clause.max_score or 0))
    if clause.score_type == "boolean":
        return (max_score if status == "passed" else Decimal("0")), True, status

    if clause.score_type == "single_choice":
        idx = sel.get("optionIndex")
        options = (clause.score_options or {}).get("options") or []
        if idx is None or idx >= len(options):
            return Decimal("0"), True, status or "pending"
        return Decimal(str(options[idx]["score"])), True, "passed"

    if clause.score_type == "multiple":
        checked = set(sel.get("subItems") or [])
        sub_items = (clause.score_options or {}).get("sub_items") or []
        total = sum(Decimal(str(s["score"])) for i, s in enumerate(sub_items) if i in checked)
        return total, True, "passed" if checked else status

    return Decimal("0"), True, status


def map_instance_to_q(db: Session, instance: FacilityModeInstance) -> dict:
    """把单个设施实例的核查结果映射到 Q 维度（设施分/系统分/控制项）"""
    category = db.query(FacilityModeCategory).filter(
        FacilityModeCategory.category_code == instance.category_code).first()
    checks = db.query(FacilityModeCheck).filter(
        FacilityModeCheck.instance_id == instance.id).all()

    results = {"facility_scores": 0, "score_items": 0, "control_checks": 0, "skipped": 0}

    # 设施类条款需要设施实体（类别有归并且建筑参评该章节时）
    facility = None
    need_facility = any((c.clause.clause_type == "facility") for c in checks if c.clause)
    if need_facility and category and category.facility_category_code:
        if instance.mapped_facility_id:
            facility = db.query(FacilityEntity).filter(
                FacilityEntity.id == instance.mapped_facility_id).first()
        if not facility:
            fc = db.query(FacilityCategory).filter(
                FacilityCategory.category_code == category.facility_category_code).first()
            if fc:
                facility = FacilityEntity(
                    building_id=instance.building_id,
                    category_id=fc.id,
                    facility_name=instance.instance_name,
                    location_description=instance.location,
                )
                db.add(facility)
                db.flush()
                instance.mapped_facility_id = facility.id

    for check in checks:
        clause = check.clause
        if not clause or not clause.standard_clause_number:
            results["skipped"] += 1
            continue

        actual, applicable, status = compute_actual_score(clause, check.selected_option)
        if status == "pending":
            results["skipped"] += 1
            continue
        now = datetime.now()

        if clause.clause_type == "facility":
            if not facility:
                results["skipped"] += 1
                continue
            results["facility_scores"] += _map_facility_clause(
                db, facility, clause, actual, applicable, check, now)
        elif clause.clause_type == "control":
            if not applicable:
                results["skipped"] += 1
                continue
            results["control_checks"] += _map_control_clause(
                db, instance.building_id, clause, status, check, now)
        else:  # system
            results["score_items"] += _map_system_clause(
                db, instance.building_id, clause, actual, applicable, check, now)

    db.commit()
    return results


def _find_standard_clause(db: Session, std_number: str) -> Optional[StandardClause]:
    """按编号找标准条文：精确 → 去字母后缀"""
    clause = db.query(StandardClause).filter(
        StandardClause.clause_number == std_number).first()
    if not clause and std_number and std_number[-1].isalpha():
        clause = db.query(StandardClause).filter(
            StandardClause.clause_number == std_number[:-1]).first()
    return clause


def _map_facility_clause(db, facility, clause, actual, applicable, check, now) -> int:
    """设施类条款 → facility_score_details（按模板子项比例分摊）"""
    from app.data.standard_data import FACILITY_CLAUSES

    base = clause.standard_clause_number
    cat_code = facility.category.category_code if facility.category else None
    template = FACILITY_CLAUSES.get(cat_code, [])
    # 匹配的模板子项：精确或前缀（5.3.1.1 -> 5.3.1.1a/b...）
    sub_tpls = [t for t in template if t["clause_number"] == base]
    if not sub_tpls:
        sub_tpls = [t for t in template if t["clause_number"].startswith(base) and
                    t["clause_number"][len(base):].isalpha()]
    if not sub_tpls:
        sub_tpls = [{"clause_number": base, "max_score": float(clause.max_score or 0)}]

    parent_max = Decimal(str(clause.max_score or 0))
    ratio = (actual / parent_max) if parent_max > 0 else Decimal("0")

    count = 0
    for tpl in sub_tpls:
        sub_max = Decimal(str(tpl["max_score"]))
        sub_actual = (sub_max * ratio).quantize(Decimal("0.01")) if applicable else Decimal("0")
        existing = db.query(FacilityScoreDetail).filter(
            FacilityScoreDetail.facility_id == facility.id,
            FacilityScoreDetail.clause_id == tpl["clause_number"]).first()
        if existing:
            existing.actual_score = sub_actual
            existing.is_applicable = applicable
            existing.is_scored = True
            existing.scored_at = now
        else:
            db.add(FacilityScoreDetail(
                facility_id=facility.id, clause_id=tpl["clause_number"],
                max_score=sub_max, applicable_score=sub_max if applicable else Decimal("0"),
                actual_score=sub_actual, is_applicable=applicable, is_scored=True,
                not_applicable_reason=None if applicable else (check.notes or "设施模式不参评"),
                scored_at=now,
            ))
            db.flush()
        count += 1
    return count


def _map_system_clause(db, building_id, clause, actual, applicable, check, now) -> int:
    """系统类条款 → system_score_details"""
    std = _find_standard_clause(db, clause.standard_clause_number)
    if not std:
        return 0
    existing = db.query(SystemScoreDetail).filter(
        SystemScoreDetail.building_id == building_id,
        SystemScoreDetail.clause_id == std.id).first()
    max_score = Decimal(str(std.max_score or clause.max_score or 0))
    # 设施模式分值可能与标准分值不同，按比例折算到标准满分
    fm_max = Decimal(str(clause.max_score or 0))
    if fm_max > 0 and max_score > 0 and fm_max != max_score:
        actual = (actual / fm_max * max_score).quantize(Decimal("0.01"))
    if existing:
        existing.actual_score = actual
        existing.is_applicable = applicable
        existing.is_scored = True
        existing.scored_at = now
        if not applicable:
            existing.not_applicable_reason = check.notes or "设施模式不参评"
    else:
        db.add(SystemScoreDetail(
            building_id=building_id, clause_id=std.id, chapter=std.chapter,
            max_score=max_score, applicable_score=max_score if applicable else Decimal("0"),
            actual_score=actual, is_applicable=applicable, is_scored=True,
            not_applicable_reason=None if applicable else (check.notes or "设施模式不参评"),
            scored_at=now,
        ))
        db.flush()
    return 1


def _map_control_clause(db, building_id, clause, status, check, now) -> int:
    """控制类条款 → control_item_checks"""
    std = _find_standard_clause(db, clause.standard_clause_number)
    if not std:
        return 0
    is_compliant = status == "passed"
    existing = db.query(ControlItemCheck).filter(
        ControlItemCheck.building_id == building_id,
        ControlItemCheck.clause_id == std.id).first()
    if existing:
        existing.is_compliant = is_compliant
        existing.check_result = check.notes or ""
        existing.checked_at = now
    else:
        db.add(ControlItemCheck(
            building_id=building_id, clause_id=std.id, chapter=std.parent_clause or "Q1",
            is_compliant=is_compliant, check_result=check.notes or "", checked_at=now,
        ))
        db.flush()
    return 1
