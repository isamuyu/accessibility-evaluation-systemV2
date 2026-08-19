"""设施评价模式 API：类别/实例/核查，保存核查后自动映射到Q维度"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import (
    FacilityModeCategory, FacilityModeClause, FacilityModeInstance,
    FacilityModeCheck, Building, StandardClause
)
from app.services.facility_mode_service import map_instance_to_q, compute_actual_score
from app.services.scoring_engine import StrategyFactory

router = APIRouter(prefix="/facility-mode", tags=["设施评价模式"])


class InstanceCreate(BaseModel):
    building_id: str
    category_code: str
    instance_name: str
    location: Optional[str] = None


class CheckInput(BaseModel):
    clause_id: str
    status: str = "pending"  # passed/failed/na/pending
    selected_option: Optional[dict] = None
    notes: Optional[str] = None


class ChecksBatch(BaseModel):
    checks: List[CheckInput]


def _std_applicability_map(db: Session) -> dict:
    """标准条文号 -> 适用建筑类型列表（设施子条款无对应条文时不过滤）"""
    return {
        c.clause_number: c.applicable_building_types
        for c in db.query(StandardClause).all()
    }


def _fm_clause_applies(clause: FacilityModeClause, std_map: dict, building_type_value: str) -> bool:
    applicable = std_map.get(clause.standard_clause_number)
    if not applicable:
        return True
    return building_type_value in applicable


def _get_instance_or_404(db: Session, instance_id: str) -> FacilityModeInstance:
    instance = db.query(FacilityModeInstance).filter(
        FacilityModeInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="设施实例不存在")
    return instance


@router.get("/categories/{building_id}")
def list_categories(building_id: str, db: Session = Depends(get_db)):
    """设施模式类别列表（含该建筑的实例数和核查进度）"""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")

    # 建筑类型参评的章节（设施模式类别按其条款章节过滤：只保留至少有一条参评章节条款的类别）
    applicable = StrategyFactory.get_strategy(building.building_type).get_applicable_chapters()
    applicable_values = {c.value for c in applicable}

    categories = db.query(FacilityModeCategory).filter(
        FacilityModeCategory.is_active == True).order_by(FacilityModeCategory.sort_order).all()
    std_map = _std_applicability_map(db)
    bt = building.building_type.value

    result = []
    for cat in categories:
        clauses = [c for c in db.query(FacilityModeClause).filter(
            FacilityModeClause.category_code == cat.category_code,
            FacilityModeClause.is_active == True,
            FacilityModeClause.chapter.in_(list(applicable_values)),
        ).all() if _fm_clause_applies(c, std_map, bt)]
        if not clauses:
            continue
        instances = db.query(FacilityModeInstance).filter(
            FacilityModeInstance.building_id == building_id,
            FacilityModeInstance.category_code == cat.category_code).all()
        checked = 0
        if instances:
            checked = db.query(FacilityModeCheck).filter(
                FacilityModeCheck.instance_id.in_([i.id for i in instances]),
                FacilityModeCheck.status != "pending").count()
        result.append({
            "category_code": cat.category_code,
            "category_name": cat.category_name,
            "facility_category_code": cat.facility_category_code,
            "clause_count": len(clauses),
            "instance_count": len(instances),
            "checked_count": checked,
        })
    return {"categories": result}


@router.post("/instances")
def create_instance(data: InstanceCreate, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == data.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    cat = db.query(FacilityModeCategory).filter(
        FacilityModeCategory.category_code == data.category_code).first()
    if not cat:
        raise HTTPException(status_code=404, detail="设施类别不存在")
    instance = FacilityModeInstance(**data.model_dump())
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/instances/{building_id}")
def list_instances(building_id: str, category_code: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(FacilityModeInstance).filter(FacilityModeInstance.building_id == building_id)
    if category_code:
        query = query.filter(FacilityModeInstance.category_code == category_code)
    return query.order_by(FacilityModeInstance.sort_order, FacilityModeInstance.created_at).all()


@router.delete("/instances/{instance_id}")
def delete_instance(instance_id: str, db: Session = Depends(get_db)):
    instance = _get_instance_or_404(db, instance_id)
    db.delete(instance)  # checks 级联删除
    db.commit()
    return {"message": "实例已删除"}


@router.get("/instances/{instance_id}/clauses")
def get_instance_clauses(instance_id: str, db: Session = Depends(get_db)):
    """实例的核查条款（含已有核查记录），按建筑类型过滤参评章节"""
    instance = _get_instance_or_404(db, instance_id)
    building = db.query(Building).filter(Building.id == instance.building_id).first()
    applicable = {c.value for c in StrategyFactory.get_strategy(building.building_type).get_applicable_chapters()}

    clauses = db.query(FacilityModeClause).filter(
        FacilityModeClause.category_code == instance.category_code,
        FacilityModeClause.is_active == True,
    ).order_by(FacilityModeClause.sort_order).all()
    std_map = _std_applicability_map(db)
    bt = building.building_type.value

    checks = {c.clause_id: c for c in db.query(FacilityModeCheck).filter(
        FacilityModeCheck.instance_id == instance_id).all()}

    result = []
    for clause in clauses:
        if clause.chapter.value not in applicable:
            continue
        if not _fm_clause_applies(clause, std_map, bt):
            continue
        check = checks.get(clause.id)
        result.append({
            "clause_id": clause.id,
            "clause_number": clause.clause_number,
            "standard_clause_number": clause.standard_clause_number,
            "clause_type": clause.clause_type,
            "title": clause.title,
            "content": clause.content,
            "max_score": clause.max_score,
            "score_type": clause.score_type,
            "score_options": clause.score_options,
            "status": check.status if check else "pending",
            "selected_option": check.selected_option if check else None,
            "notes": check.notes if check else None,
        })
    return {"instance_name": instance.instance_name, "clauses": result}


@router.post("/instances/{instance_id}/checks")
def save_checks(instance_id: str, data: ChecksBatch, db: Session = Depends(get_db)):
    """保存核查结果并自动映射到Q维度"""
    instance = _get_instance_or_404(db, instance_id)
    clause_ids = {c.clause_id for c in data.checks}
    clauses = {c.id: c for c in db.query(FacilityModeClause).filter(
        FacilityModeClause.id.in_(clause_ids)).all()}

    now = datetime.now()
    for item in data.checks:
        clause = clauses.get(item.clause_id)
        if not clause:
            continue
        actual, applicable, status = compute_actual_score(clause, item.selected_option)
        existing = db.query(FacilityModeCheck).filter(
            FacilityModeCheck.instance_id == instance_id,
            FacilityModeCheck.clause_id == item.clause_id).first()
        if existing:
            existing.status = status
            existing.selected_option = item.selected_option
            existing.auto_score = actual
            existing.notes = item.notes
            existing.checked_at = now
        else:
            db.add(FacilityModeCheck(
                instance_id=instance_id, clause_id=item.clause_id,
                status=status, selected_option=item.selected_option,
                auto_score=actual, notes=item.notes, checked_at=now,
            ))
    db.flush()

    # 自动映射到Q维度
    map_result = map_instance_to_q(db, instance)
    return {"message": "保存成功", "mapped": map_result}


@router.get("/coverage/{building_id}")
def get_coverage(building_id: str, db: Session = Depends(get_db)):
    """设施模式覆盖情况：哪些应评条款未被设施模式覆盖（需回普通模式完成）"""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")

    applicable = {c.value for c in StrategyFactory.get_strategy(building.building_type).get_applicable_chapters()}
    chapters = set(applicable) | {"maintenance"}
    if building.is_within_one_year:
        chapters.add("construction")

    # 设施模式覆盖的标准条款号（含去字母后缀匹配）
    fm_numbers = {r[0] for r in db.query(FacilityModeClause.standard_clause_number).filter(
        FacilityModeClause.is_active == True,
        FacilityModeClause.standard_clause_number.isnot(None)).all()}

    def covered(num: str) -> bool:
        if num in fm_numbers:
            return True
        # 设施模式条款号可能带字母后缀，标准条文也可能带（5.3.x 类）
        base = num[:-1] if num and num[-1].isalpha() else num
        return base in fm_numbers

    # 应评的标准条文：参评章节 + 建筑类型适用 + 有分值或为控制项
    clauses = db.query(StandardClause).filter(StandardClause.is_active == True).all()
    bt = building.building_type.value
    by_chapter = {}
    covered_count = 0
    for c in clauses:
        ch = c.chapter.value
        if ch == "control":
            # 控制项按 parent（Q1-Q4/construction/maintenance）过滤
            parent = c.parent_clause
            if parent not in chapters:
                continue
        elif ch not in chapters:
            continue
        if c.applicable_building_types and bt not in c.applicable_building_types:
            continue
        if c.clause_type.value == "control":
            key = c.parent_clause or "control"
        else:
            key = ch
        if covered(c.clause_number):
            covered_count += 1
            continue
        entry = by_chapter.setdefault(key, {"chapter": key, "uncovered": 0, "examples": []})
        entry["uncovered"] += 1
        if len(entry["examples"]) < 3:
            entry["examples"].append(c.clause_number)

    uncovered_list = sorted(by_chapter.values(), key=lambda x: x["chapter"])
    return {
        "building_id": building_id,
        "covered": covered_count,
        "uncovered": sum(e["uncovered"] for e in uncovered_list),
        "by_chapter": uncovered_list,
    }


@router.get("/progress/{building_id}")
def get_progress(building_id: str, db: Session = Depends(get_db)):
    """设施模式总进度（分母=所有实例的参评条款数）"""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    instances = db.query(FacilityModeInstance).filter(
        FacilityModeInstance.building_id == building_id).all()
    if not instances:
        return {"total": 0, "checked": 0, "progress": 0}

    applicable = {c.value for c in StrategyFactory.get_strategy(building.building_type).get_applicable_chapters()}
    total = 0
    for inst in instances:
        total += db.query(FacilityModeClause).filter(
            FacilityModeClause.category_code == inst.category_code,
            FacilityModeClause.is_active == True,
            FacilityModeClause.chapter.in_(list(applicable)),
        ).count()
    checked = db.query(FacilityModeCheck).filter(
        FacilityModeCheck.instance_id.in_([i.id for i in instances]),
        FacilityModeCheck.status != "pending").count()
    return {
        "total": total, "checked": checked,
        "progress": round(checked / total * 100, 1) if total else 0,
    }
