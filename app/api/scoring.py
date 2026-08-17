from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from decimal import Decimal
import hashlib
import json
from app.core.database import get_db
from app.core.enums import *
from app.models.models import StandardClause
from app.schemas.schemas import *
from app.services.crud import *
from app.services.scoring_engine import ScoringEngine, ScoreItem, Facility, StrategyFactory

router = APIRouter(prefix="/scoring", tags=["评分管理"])

# 无设施数据时的中性设施分（Q = S × F/10，F=10 表示不折减）
NEUTRAL_FACILITY_SCORE = Decimal("10")


def _to_score_items(rows) -> List[ScoreItem]:
    return [ScoreItem(
        clause=item.clause_id,
        description="",
        max_score=item.max_score,
        actual_score=item.actual_score,
        applicable=item.is_applicable
    ) for item in rows]


def _compute_source_hash(building, control_items, system_scores, facilities) -> str:
    """对评价输入数据计算哈希，用于幂等判断（含建筑属性：类型/完工时间/现场检测）"""
    payload = {
        "building": [
            building.building_type.value,
            bool(building.is_within_one_year),
            building.site_inspection_passed,
        ],
        "control": sorted(
            [str(c.clause_id), c.is_compliant] for c in control_items
        ),
        "system": sorted(
            [str(s.clause_id), str(s.max_score), str(s.actual_score), bool(s.is_applicable), bool(getattr(s, "is_scored", True))]
            for s in system_scores
        ),
        "facility": sorted(
            [str(f.id), str(fs.clause_id), str(fs.max_score), str(fs.actual_score), bool(fs.is_applicable), bool(getattr(fs, "is_scored", True))]
            for f in facilities for fs in f.score_items
        ),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()


def _group_facilities_by_chapter(facilities) -> Dict[Chapter, Dict[str, List[Facility]]]:
    """按章节 -> 设施类别分组，用于分别计算 F1/F2/F3"""
    chapter_groups: Dict[Chapter, Dict[str, List[Facility]]] = {}
    for facility in facilities:
        if not facility.category:
            continue
        chapter = facility.category.chapter
        category = facility.category.category_code
        f_items = _to_score_items(facility.score_items)
        chapter_groups.setdefault(chapter, {}).setdefault(category, []).append(Facility(
            id=facility.id,
            category=category,
            location=facility.location_description or "",
            score_items=f_items
        ))
    return chapter_groups

# ========== 控制项管理 ==========
@router.post("/control-items/{building_id}", response_model=ControlItemCheckResponse)
def create_control_item(building_id: str, item: ControlItemCheckCreate, db: Session = Depends(get_db)):
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return ControlItemService.create(db, building_id, item)

@router.get("/control-items/{building_id}", response_model=List[ControlItemCheckResponse])
def list_control_items(building_id: str, db: Session = Depends(get_db)):
    items = db.query(ControlItemCheck, StandardClause).join(
        StandardClause, ControlItemCheck.clause_id == StandardClause.id
    ).filter(ControlItemCheck.building_id == building_id).all()
    
    result = []
    for item, clause in items:
        result.append({
            "id": item.id,
            "building_id": item.building_id,
            "clause_id": item.clause_id,
            "clause_number": clause.clause_number,
            "description": clause.description,
            "applicable_building_types": clause.applicable_building_types,
            "chapter": item.chapter,
            "is_compliant": item.is_compliant,
            "check_result": item.check_result,
            "checked_by": item.checked_by,
            "checked_at": item.checked_at
        })
    return result

@router.put("/control-items/{item_id}", response_model=ControlItemCheckResponse)
def update_control_item(item_id: str, item: ControlItemCheckUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(ControlItemCheck).filter(ControlItemCheck.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="控制项不存在")
    return ControlItemService.update(db, db_obj, item)

@router.delete("/control-items/{item_id}")
def delete_control_item(item_id: str, db: Session = Depends(get_db)):
    db_obj = db.query(ControlItemCheck).filter(ControlItemCheck.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="控制项不存在")
    db.delete(db_obj)
    db.commit()
    return {"message": "控制项已删除"}

# ========== 系统评分管理 ==========
@router.post("/system-scores/{building_id}", response_model=SystemScoreDetailResponse)
def create_system_score(building_id: str, item: SystemScoreDetailCreate, db: Session = Depends(get_db)):
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return SystemScoreService.create(db, building_id, item)

@router.get("/system-scores/{building_id}", response_model=List[SystemScoreDetailResponse])
def list_system_scores(building_id: str, chapter: Optional[Chapter] = None, db: Session = Depends(get_db)):
    query = db.query(SystemScoreDetail, StandardClause).join(
        StandardClause, SystemScoreDetail.clause_id == StandardClause.id
    ).filter(SystemScoreDetail.building_id == building_id)
    
    if chapter:
        query = query.filter(SystemScoreDetail.chapter == chapter)
    
    items = query.all()
    
    result = []
    for item, clause in items:
        result.append({
            "id": item.id,
            "building_id": item.building_id,
            "clause_id": item.clause_id,
            "clause_number": clause.clause_number,
            "description": clause.description,
            "options": clause.options,
            "applicable_building_types": clause.applicable_building_types,
            "chapter": item.chapter,
            "max_score": item.max_score,
            "applicable_score": item.applicable_score,
            "actual_score": item.actual_score,
            "is_applicable": item.is_applicable,
            "is_scored": item.is_scored,
            "scored_by": item.scored_by,
            "scored_at": item.scored_at
        })
    return result

@router.put("/system-scores/{item_id}", response_model=SystemScoreDetailResponse)
def update_system_score(item_id: str, item: ScoreItemUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(SystemScoreDetail).filter(SystemScoreDetail.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="评分项不存在")
    update_data = item.model_dump(exclude_unset=True)
    if item.actual_score is not None:
        if item.actual_score < 0:
            raise HTTPException(status_code=400, detail="实际得分不能为负数")
        if item.actual_score > db_obj.max_score:
            raise HTTPException(status_code=400, detail="实际得分不能超过满分")
        update_data["is_scored"] = True
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/system-scores/{item_id}")
def delete_system_score(item_id: str, db: Session = Depends(get_db)):
    db_obj = db.query(SystemScoreDetail).filter(SystemScoreDetail.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="评分项不存在")
    db.delete(db_obj)
    db.commit()
    return {"message": "评分项已删除"}

# ========== 设施管理 ==========
@router.post("/facilities/{building_id}", response_model=FacilityEntityResponse)
def create_facility(building_id: str, facility: FacilityEntityCreate, db: Session = Depends(get_db)):
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    return FacilityService.create(db, building_id, facility)

@router.get("/facilities/{building_id}", response_model=List[FacilityEntityResponse])
def list_facilities(building_id: str, db: Session = Depends(get_db)):
    return FacilityService.get_by_building(db, building_id)

@router.post("/facilities/{facility_id}/scores", response_model=FacilityScoreDetailResponse)
def create_facility_score(facility_id: str, item: FacilityScoreItemCreate, db: Session = Depends(get_db)):
    facility = FacilityService.get(db, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="设施不存在")
    return FacilityService.create_score_item(db, facility_id, item)

@router.delete("/facilities/{facility_id}")
def delete_facility(facility_id: str, db: Session = Depends(get_db)):
    facility = FacilityService.get(db, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="设施不存在")
    db.query(FacilityScoreDetail).filter(FacilityScoreDetail.facility_id == facility_id).delete()
    db.delete(facility)
    db.commit()
    return {"message": "设施已删除"}

@router.get("/facilities/{facility_id}/scores", response_model=List[FacilityScoreDetailResponse])
def list_facility_scores(facility_id: str, db: Session = Depends(get_db)):
    facility = FacilityService.get(db, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="设施不存在")
    items = FacilityService.get_score_items(db, facility_id)

    # 从设施条文模板补充条文描述和选项（clause_id 存的是条文编号）
    from app.data.standard_data import FACILITY_CLAUSES
    desc_map = {
        c["clause_number"]: c
        for clauses in FACILITY_CLAUSES.values() for c in clauses
    }
    return [
        {**{k: getattr(i, k) for k in ("id", "facility_id", "clause_id", "max_score", "applicable_score", "actual_score", "is_applicable", "is_scored")},
         "description": desc_map.get(i.clause_id, {}).get("description"),
         "options": desc_map.get(i.clause_id, {}).get("options")}
        for i in items
    ]

@router.put("/facilities/scores/{score_id}", response_model=FacilityScoreDetailResponse)
def update_facility_score(score_id: str, item: ScoreItemUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(FacilityScoreDetail).filter(FacilityScoreDetail.id == score_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="设施评分项不存在")
    update_data = item.model_dump(exclude_unset=True)
    if item.actual_score is not None:
        if item.actual_score < 0:
            raise HTTPException(status_code=400, detail="实际得分不能为负数")
        if item.actual_score > db_obj.max_score:
            raise HTTPException(status_code=400, detail="实际得分不能超过满分")
        update_data["is_scored"] = True
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/facilities/scores/{score_id}")
def delete_facility_score(score_id: str, db: Session = Depends(get_db)):
    db_obj = db.query(FacilityScoreDetail).filter(FacilityScoreDetail.id == score_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="设施评分项不存在")
    db.delete(db_obj)
    db.commit()
    return {"message": "设施评分项已删除"}

# ========== 核心评分计算 ==========
@router.post("/evaluate/{building_id}", response_model=EvaluationResult)
def evaluate_building(building_id: str, db: Session = Depends(get_db)):
    """执行完整评价计算"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")

    # Step 1: 检查控制项
    control_items = ControlItemService.get_by_building(db, building_id)
    if not control_items:
        return EvaluationResult(
            building_id=building_id,
            eligible=False,
            reason="未录入控制项核查记录，无法评价"
        )

    # 条文级适用性过滤：不适用该建筑类型的条文（如5.2.1.3仅公共建筑）不参与评价
    building_type = building.building_type
    all_clause_ids = {i.clause_id for i in control_items}
    all_clause_ids |= {i.clause_id for i in SystemScoreService.get_by_building(db, building_id)}
    clause_map = {
        c.id: c for c in db.query(StandardClause).filter(StandardClause.id.in_(all_clause_ids)).all()
    } if all_clause_ids else {}

    def item_applies(item) -> bool:
        clause = clause_map.get(item.clause_id)
        if not clause or not clause.applicable_building_types:
            return True
        return building_type.value in clause.applicable_building_types

    control_items = [i for i in control_items if item_applies(i)]
    if not control_items:
        return EvaluationResult(
            building_id=building_id,
            eligible=False,
            reason="无适用于该建筑类型的控制项核查记录，无法评价"
        )
    control_list = [{"clause_id": item.clause_id, "is_compliant": item.is_compliant} for item in control_items]

    passed, reason = ScoringEngine.check_control_items(control_list)
    if not passed:
        # 记录未通过结果（含幂等），避免结果页停留在旧等级
        fail_hash = _compute_source_hash(building, control_items, [], [])
        latest = DimensionScoreService.get_latest(db, building_id)
        if not (latest and latest.source_data_hash == fail_hash
                and latest.determined_grade == Grade.NONE):
            DimensionScoreService.create(db, building_id, {
                "determined_grade": Grade.NONE,
                "breakdown": {"reason": reason},
                "source_data_hash": fail_hash,
            })
        return EvaluationResult(
            building_id=building_id,
            eligible=False,
            reason=reason
        )

    # 设施数据检查：无设施实体会导致 Q = S × (F/10) 中 F=0，评价无意义
    all_facilities = FacilityService.get_by_building(db, building_id)
    if not all_facilities:
        return EvaluationResult(
            building_id=building_id,
            eligible=False,
            reason="未录入设施数据，无法评价"
        )
    chapter_groups = _group_facilities_by_chapter(all_facilities)

    def facility_score_for(chapter: Chapter) -> Decimal:
        groups = chapter_groups.get(chapter)
        if not groups:
            return NEUTRAL_FACILITY_SCORE
        return ScoringEngine.calc_facility_score(groups)

    # Step 2-4: 计算各维度分
    scores = {}
    applicable_chapters = StrategyFactory.get_strategy(building_type).get_applicable_chapters()

    def chapter_items(chapter: Chapter):
        return [i for i in SystemScoreService.get_by_building_and_chapter(db, building_id, chapter)
                if item_applies(i)]

    # Q1 无障碍通行
    S1 = ScoringEngine.calc_system_score(_to_score_items(chapter_items(Chapter.Q1)))
    F1 = facility_score_for(Chapter.Q1)
    Q1 = ScoringEngine.calc_Qx(S1, F1)
    scores["Q1"] = Q1

    # Q2 公共无障碍服务 / Q3 无障碍住宿（按建筑类型参评）
    S2 = F2 = Q2 = None
    S3 = F3 = Q3 = None

    if Chapter.Q2 in applicable_chapters:
        S2 = ScoringEngine.calc_system_score(_to_score_items(chapter_items(Chapter.Q2)))
        F2 = facility_score_for(Chapter.Q2)
        Q2 = ScoringEngine.calc_Qx(S2, F2)
        scores["Q2"] = Q2

    if Chapter.Q3 in applicable_chapters:
        S3 = ScoringEngine.calc_system_score(_to_score_items(chapter_items(Chapter.Q3)))
        F3 = facility_score_for(Chapter.Q3)
        Q3 = ScoringEngine.calc_Qx(S3, F3)
        scores["Q3"] = Q3

    # Q4 信息交流
    Q4 = ScoringEngine.calc_Q4(_to_score_items(chapter_items(Chapter.Q4)))
    scores["Q4"] = Q4

    # Q5 创新提升
    Q5 = ScoringEngine.calc_Q5(_to_score_items(chapter_items(Chapter.Q5)))
    scores["Q5"] = Q5

    # 施工验收（仅竣工一年内评价，表2/表3）和运行维护
    if building.is_within_one_year:
        construction_score = ScoringEngine.calc_construction_score(_to_score_items(chapter_items(Chapter.CONSTRUCTION)))
    else:
        construction_score = None
    maintenance_score = ScoringEngine.calc_maintenance_score(_to_score_items(chapter_items(Chapter.MAINTENANCE)))
    
    # 计算总分
    total_Q = ScoringEngine.calc_total_Q(building_type, scores)
    
    # 等级认定
    grade, breakdown = ScoringEngine.determine_grade(
        Q=total_Q,
        q1=Q1,
        q2=Q2,
        q3=Q3,
        q4=Q4,
        construction_score=construction_score if construction_score is not None else Decimal("0"),
        maintenance_score=maintenance_score,
        within_one_year=building.is_within_one_year,
        site_inspection_passed=building.site_inspection_passed
    )
    
    # 保存结果（幂等：输入数据未变化时不重复插入）
    source_hash = _compute_source_hash(
        building,
        control_items,
        [i for i in SystemScoreService.get_by_building(db, building_id) if item_applies(i)],
        all_facilities
    )
    result_data = {
        "q1_system_score": S1,
        "q1_facility_score": F1,
        "q1_score": Q1,
        "q2_system_score": S2,
        "q2_facility_score": F2,
        "q2_score": Q2,
        "q3_system_score": S3,
        "q3_facility_score": F3,
        "q3_score": Q3,
        "q4_score": Q4,
        "q5_score": Q5,
        "construction_score": construction_score,
        "maintenance_score": maintenance_score,
        "total_score_q": total_Q,
        "determined_grade": grade,
        "breakdown": breakdown,
        "source_data_hash": source_hash,
    }

    latest = DimensionScoreService.get_latest(db, building_id)
    if not (latest and latest.source_data_hash == source_hash):
        DimensionScoreService.create(db, building_id, result_data)
    
    return EvaluationResult(
        building_id=building_id,
        eligible=True,
        grade=grade,
        total_score_q=total_Q,
        q1_score=Q1,
        q2_score=Q2,
        q3_score=Q3,
        q4_score=Q4,
        q5_score=Q5,
        construction_score=construction_score,
        maintenance_score=maintenance_score,
        breakdown=breakdown
    )

# ========== 建筑群综合评分 ==========
@router.post("/complex/{project_id}", response_model=ComplexBuildingScoreResponse)
def evaluate_complex_building(project_id: str, z2_score: Optional[Decimal] = None, db: Session = Depends(get_db)):
    """建筑群综合评价（4.2.1.10）

    z2_score: 可选，整体建筑区域无障碍通行评分（按4.2.1.6计算，单体出入口及内部交通不参评），默认80。
    前提：每个单体建筑均已评价且 Q≥40；Q1-Q4/施工验收/运行维护按面积比例加权；
    等级按表2（任一建筑竣工一年内）或表3确定。
    """
    project = ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if z2_score is not None and not (Decimal("0") <= z2_score <= Decimal("100")):
        raise HTTPException(status_code=400, detail="Z2分值必须在0到100之间")

    buildings = BuildingService.get_by_project(db, project_id)
    if not buildings:
        raise HTTPException(status_code=400, detail="项目下没有建筑")

    building_list = []
    for b in buildings:
        latest = DimensionScoreService.get_latest(db, b.id)
        if not latest:
            raise HTTPException(status_code=400, detail=f"建筑 {b.building_name} 尚未评价，请先执行评价计算")
        building_list.append({
            "id": b.id,
            "name": b.building_name,
            "Q": latest.total_score_q or Decimal("0"),
            "floor_area": b.floor_area or Decimal("0"),
            "q1": latest.q1_score, "q2": latest.q2_score, "q3": latest.q3_score, "q4": latest.q4_score,
            "construction": latest.construction_score, "maintenance": latest.maintenance_score,
        })

    # 建筑群：任一建筑一年内→按表2；全部一年后→按表3且须全部现场检测合格
    within_one_year = any(b.is_within_one_year for b in buildings)
    site_inspection = all(b.site_inspection_passed is True for b in buildings)

    try:
        result = ScoringEngine.calc_complex_full(
            building_list, z2=z2_score,
            within_one_year=within_one_year,
            site_inspection_passed=site_inspection,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = ComplexScoreService.create(
        db, project_id,
        result["z1"], result["z2"], result["zq"],
        result["building_scores"],
        dimension_scores={k: str(v) for k, v in result["dimensions"].items() if v is not None},
        determined_grade=result["grade"],
        breakdown=result["breakdown"],
    )
    return record

@router.get("/complex/{project_id}", response_model=ComplexBuildingScoreResponse)
def get_complex_building_score(project_id: str, db: Session = Depends(get_db)):
    """查询建筑群最新综合评价结果"""
    result = ComplexScoreService.get_by_project(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="该项目尚无建筑群评价结果")
    return result

# ========== 查询评分结果 ==========
@router.get("/results/{building_id}", response_model=List[DimensionScoreResponse])
def get_evaluation_results(building_id: str, db: Session = Depends(get_db)):
    return DimensionScoreService.get_by_building(db, building_id)