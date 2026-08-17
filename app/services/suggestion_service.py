"""改善建议服务：以提升星级为首要目标，改造难度（优先级）次之"""
from decimal import Decimal
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.enums import Grade
from app.models.models import (
    Building, ControlItemCheck, SystemScoreDetail, FacilityScoreDetail,
    FacilityEntity, StandardClause, DimensionScore
)
from app.data.priority_data import lookup_priority, PRIORITY_CATEGORIES
from app.services.crud import DimensionScoreService

# 各级别门槛：各维度最低分 / 总Q / 施工验收与运行维护
GRADE_THRESHOLDS = {
    Grade.ONE_STAR: {"min_q": Decimal("20"), "total_q": Decimal("40"), "aux": Decimal("60")},
    Grade.TWO_STAR: {"min_q": Decimal("40"), "total_q": Decimal("60"), "aux": Decimal("70")},
    Grade.THREE_STAR: {"min_q": Decimal("60"), "total_q": Decimal("80"), "aux": Decimal("80")},
}
GRADE_ORDER = [Grade.NONE, Grade.ONE_STAR, Grade.TWO_STAR, Grade.THREE_STAR]
GRADE_LABELS = {
    Grade.NONE: "未达标", Grade.ONE_STAR: "一星级",
    Grade.TWO_STAR: "二星级", Grade.THREE_STAR: "三星级",
}
DIMENSION_LABELS = {
    "Q1": "Q1 无障碍通行", "Q2": "Q2 公共无障碍服务", "Q3": "Q3 无障碍住宿",
    "Q4": "Q4 信息交流与智慧服务", "Q5": "Q5 创新与提升",
    "construction": "施工验收", "maintenance": "运行维护",
}


def _chapter_of_clause(clause_number: str) -> str:
    if not clause_number:
        return ""
    first = clause_number.split(".")[0]
    return {"5": "Q1", "6": "Q2", "7": "Q3", "Q3": "Q3", "8": "Q4",
            "9": "construction", "10": "maintenance", "11": "Q5"}.get(first, "")


def _analyze_grade_gap(building: Building, score: Optional[DimensionScore]) -> Dict[str, Any]:
    """分析当前等级与下一级目标的差距，返回短板维度集合"""
    current = score.determined_grade if score and score.determined_grade else Grade.NONE
    idx = GRADE_ORDER.index(current)
    if idx >= len(GRADE_ORDER) - 1 or score is None:
        return {"current_grade": current.value, "target_grade": None, "blocking": [], "total_q_gap": None}

    target = GRADE_ORDER[idx + 1]
    th = GRADE_THRESHOLDS[target]
    blocking = []

    # 各维度最低分门槛（Q1-Q4，不参评维度除外）
    for dim, field in [("Q1", "q1_score"), ("Q2", "q2_score"), ("Q3", "q3_score"), ("Q4", "q4_score")]:
        val = getattr(score, field)
        if val is not None and val < th["min_q"]:
            blocking.append({
                "dimension": dim, "label": DIMENSION_LABELS[dim],
                "current": float(val), "required": float(th["min_q"]),
                "gap": float(th["min_q"] - val),
            })

    # 施工验收（一年内）/ 运行维护门槛
    if building.is_within_one_year and score.construction_score is not None \
            and score.construction_score < th["aux"]:
        blocking.append({
            "dimension": "construction", "label": "施工验收",
            "current": float(score.construction_score), "required": float(th["aux"]),
            "gap": float(th["aux"] - score.construction_score),
        })
    if score.maintenance_score is not None and score.maintenance_score < th["aux"]:
        blocking.append({
            "dimension": "maintenance", "label": "运行维护",
            "current": float(score.maintenance_score), "required": float(th["aux"]),
            "gap": float(th["aux"] - score.maintenance_score),
        })

    total_q_gap = None
    if score.total_score_q is not None and score.total_score_q < th["total_q"]:
        total_q_gap = {"current": float(score.total_score_q), "required": float(th["total_q"]),
                       "gap": float(th["total_q"] - score.total_score_q)}

    # 竣工一年后：现场检测合格是评级前提（表3）
    if not building.is_within_one_year and building.site_inspection_passed is not True:
        blocking.append({
            "dimension": "site_inspection", "label": "现场检测",
            "current": 0, "required": 1, "gap": 1,
        })

    return {
        "current_grade": current.value,
        "current_grade_label": GRADE_LABELS[current],
        "target_grade": target.value,
        "target_grade_label": GRADE_LABELS[target],
        "blocking": blocking,
        "blocking_dimensions": [b["dimension"] for b in blocking],
        "total_q_gap": total_q_gap,
    }


def build_improvement_suggestions(db: Session, building_id: str) -> Dict[str, Any]:
    """生成改善建议：升星短板优先，同级按改造优先级（难度）排序"""
    building = db.query(Building).filter(Building.id == building_id).first()
    score = DimensionScoreService.get_latest(db, building_id)
    analysis = _analyze_grade_gap(building, score) if building else {"blocking_dimensions": []}
    blocking_dims = set(analysis.get("blocking_dimensions", []))

    suggestions = []

    # 现场检测（竣工一年后评级前提，表3）
    if building and not building.is_within_one_year and building.site_inspection_passed is not True:
        suggestions.append({
            "stars": 5,
            "category": PRIORITY_CATEGORIES[5],
            "content": "按GB50642对无障碍设施性能进行现场检测并合格（竣工一年后评价前提）",
            "clause_number": "表3",
            "description": "",
            "dimension": "site_inspection",
            "dimension_label": "现场检测",
            "lost_score": None,
            "status": "未检测或未合格",
            "is_key": True,
        })

    # 控制项：未达标/未核查 → 最高优先（一票否决）
    control_items = db.query(ControlItemCheck).filter(
        ControlItemCheck.building_id == building_id).all()
    clause_ids = [i.clause_id for i in control_items]
    clause_map = {c.id: c for c in db.query(StandardClause).filter(
        StandardClause.id.in_(clause_ids)).all()} if clause_ids else {}
    for item in control_items:
        if item.is_compliant is True:
            continue
        clause = clause_map.get(item.clause_id)
        suggestions.append({
            "stars": 5,
            "category": PRIORITY_CATEGORIES[5],
            "content": "控制项必须达标（不达标不予评级）",
            "clause_number": clause.clause_number if clause else item.clause_id,
            "description": clause.description if clause else "",
            "dimension": item.chapter.value if item.chapter else "",
            "dimension_label": DIMENSION_LABELS.get(item.chapter.value if item.chapter else "", ""),
            "lost_score": None,
            "status": "未达标" if item.is_compliant is False else "未核查",
            "is_key": True,
        })

    # 系统评分失分项
    system_items = db.query(SystemScoreDetail).filter(
        SystemScoreDetail.building_id == building_id,
        SystemScoreDetail.is_applicable == True,
        SystemScoreDetail.is_scored == True,
    ).all()
    sys_clause_map = {c.id: c for c in db.query(StandardClause).filter(
        StandardClause.id.in_([i.clause_id for i in system_items])).all()} if system_items else {}
    for item in system_items:
        lost = (item.max_score or Decimal("0")) - (item.actual_score or Decimal("0"))
        if lost <= 0:
            continue
        clause = sys_clause_map.get(item.clause_id)
        clause_number = clause.clause_number if clause else item.clause_id
        content, stars = lookup_priority(clause_number)
        dim = item.chapter.value if item.chapter else _chapter_of_clause(clause_number)
        suggestions.append({
            "stars": stars,
            "category": PRIORITY_CATEGORIES[stars],
            "content": content or (clause.description if clause else ""),
            "clause_number": clause_number,
            "description": clause.description if clause else "",
            "dimension": dim,
            "dimension_label": DIMENSION_LABELS.get(dim, dim),
            "lost_score": float(lost),
            "status": f"得 {item.actual_score}/{item.max_score} 分",
            "is_key": dim in blocking_dims,
        })

    # 设施评分失分项
    facility_ids = [f.id for f in db.query(FacilityEntity).filter(
        FacilityEntity.building_id == building_id).all()]
    if facility_ids:
        facility_items = db.query(FacilityScoreDetail).filter(
            FacilityScoreDetail.facility_id.in_(facility_ids),
            FacilityScoreDetail.is_applicable == True,
            FacilityScoreDetail.is_scored == True,
        ).all()
        for item in facility_items:
            lost = (item.max_score or Decimal("0")) - (item.actual_score or Decimal("0"))
            if lost <= 0:
                continue
            content, stars = lookup_priority(item.clause_id)
            if not content:
                from app.data.standard_data import FACILITY_CLAUSES
                content = next(
                    (c["description"] for clauses in FACILITY_CLAUSES.values()
                     for c in clauses if c["clause_number"] == item.clause_id), "")
            dim = _chapter_of_clause(item.clause_id)
            suggestions.append({
                "stars": stars,
                "category": PRIORITY_CATEGORIES[stars],
                "content": content,
                "clause_number": item.clause_id,
                "description": "",
                "dimension": dim,
                "dimension_label": DIMENSION_LABELS.get(dim, dim),
                "lost_score": float(lost),
                "status": f"设施项得 {item.actual_score}/{item.max_score} 分",
                "is_key": dim in blocking_dims,
            })

    # 排序：升星关键项优先 → 改造优先级（难度）→ 失分
    # 若仅总Q不达标（无短板维度），Q1-Q4失分项都算升星关键
    only_total_gap = (not blocking_dims) and analysis.get("total_q_gap")
    if only_total_gap:
        for sg in suggestions:
            if sg["dimension"] in ("Q1", "Q2", "Q3", "Q4"):
                sg["is_key"] = True
    suggestions.sort(key=lambda x: (not x["is_key"], -x["stars"], -(x["lost_score"] or 0)))

    return {
        "analysis": analysis,
        "suggestions": suggestions,
        "priority_categories": PRIORITY_CATEGORIES,
    }
