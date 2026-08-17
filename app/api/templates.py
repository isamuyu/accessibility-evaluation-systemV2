from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.core.enums import *
from app.models.models import (
    StandardClause, Building, ControlItemCheck, SystemScoreDetail, FacilityScoreDetail
)
from app.schemas.schemas import *
from app.services.crud import *
from app.services.scoring_engine import StrategyFactory

router = APIRouter(prefix="/templates", tags=["评价模板"])


def _applies_to_building_type(clause: StandardClause, building_type: BuildingType) -> bool:
    """根据条文的 applicable_building_types 判断是否适用于该建筑类型"""
    applicable = clause.applicable_building_types
    if not applicable:
        return True
    return building_type.value in applicable

@router.post("/generate-control-items/{building_id}")
def generate_control_items(building_id: str, db: Session = Depends(get_db)):
    """根据建筑类型自动生成控制项"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    
    # 获取该建筑类型应参评的控制项章节（Q1-Q4，规则统一来自评分策略）
    building_type = building.building_type
    strategy = StrategyFactory.get_strategy(building_type)
    applicable_parents = [
        ch.value for ch in strategy.get_applicable_chapters() if ch != Chapter.Q5
    ]
    # 运行维护控制项均参评；施工验收控制项仅竣工一年内项目参评（表2/表3）
    applicable_parents.append(Chapter.MAINTENANCE.value)
    if building.is_within_one_year:
        applicable_parents.append(Chapter.CONSTRUCTION.value)
    
    # 查询标准控制项
    clauses = db.query(StandardClause).filter(
        StandardClause.chapter == Chapter.CONTROL,
        StandardClause.clause_type == ClauseType.CONTROL,
        StandardClause.is_active == True,
        StandardClause.parent_clause.in_(applicable_parents)
    ).order_by(StandardClause.sort_order).all()
    
    created_items = []
    for clause in clauses:
        # 按条文的适用建筑类型过滤
        if not _applies_to_building_type(clause, building_type):
            continue
        # 检查是否已存在
        existing = db.query(ControlItemCheck).filter(
            ControlItemCheck.building_id == building_id,
            ControlItemCheck.clause_id == clause.id
        ).first()
        
        if not existing:
            item = ControlItemCheck(
                building_id=building_id,
                clause_id=clause.id,
                chapter=clause.parent_clause,
                is_compliant=None,  # 未检查
                check_result=""
            )
            db.add(item)
            created_items.append({
                "clause_id": clause.clause_number,
                "description": clause.description,
                "chapter": clause.parent_clause
            })
    
    db.commit()
    return {
        "message": f"已生成 {len(created_items)} 条控制项",
        "items": created_items
    }

@router.post("/generate-system-scores/{building_id}")
def generate_system_scores(building_id: str, db: Session = Depends(get_db)):
    """根据建筑类型自动生成系统评分项"""
    building = BuildingService.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="建筑不存在")
    
    # 获取该建筑类型应参评的章节（规则统一来自评分策略）
    # 运行维护均参评；施工验收仅竣工一年内项目参评（表2/表3）
    building_type = building.building_type
    strategy = StrategyFactory.get_strategy(building_type)
    applicable_chapters = strategy.get_applicable_chapters() + [Chapter.MAINTENANCE]
    if building.is_within_one_year:
        applicable_chapters.append(Chapter.CONSTRUCTION)
    
    # 查询标准系统评分项（含Q5创新与提升的bonus类型）
    clauses = db.query(StandardClause).filter(
        StandardClause.chapter.in_(applicable_chapters),
        StandardClause.clause_type.in_([ClauseType.SYSTEM, ClauseType.BONUS]),
        StandardClause.is_active == True,
        StandardClause.max_score > 0
    ).order_by(StandardClause.chapter, StandardClause.sort_order).all()
    
    created_items = []
    for clause in clauses:
        # 按条文的适用建筑类型过滤
        if not _applies_to_building_type(clause, building_type):
            continue
        # 检查是否已存在
        existing = db.query(SystemScoreDetail).filter(
            SystemScoreDetail.building_id == building_id,
            SystemScoreDetail.clause_id == clause.id
        ).first()
        
        if not existing:
            item = SystemScoreDetail(
                building_id=building_id,
                clause_id=clause.id,
                chapter=clause.chapter,
                max_score=clause.max_score,
                applicable_score=clause.max_score,  # 默认全部参评
                actual_score=Decimal("0"),
                is_applicable=True
            )
            db.add(item)
            created_items.append({
                "clause_id": clause.clause_number,
                "description": clause.description,
                "chapter": clause.chapter.value,
                "max_score": float(clause.max_score)
            })
    
    db.commit()
    return {
        "message": f"已生成 {len(created_items)} 条系统评分项",
        "items": created_items
    }

@router.post("/generate-facility-scores/{facility_id}")
def generate_facility_scores(facility_id: str, db: Session = Depends(get_db)):
    """根据设施类别自动生建设施评分项"""
    facility = FacilityService.get(db, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="设施不存在")
    
    category_code = facility.category.category_code if facility.category else None
    if not category_code:
        raise HTTPException(status_code=400, detail="设施类别未知")
    
    from app.data.standard_data import FACILITY_CLAUSES
    
    facility_clauses = FACILITY_CLAUSES.get(category_code, [])
    if not facility_clauses:
        return {"message": "该设施类别暂无标准评分项", "items": []}
    
    created_items = []
    for clause_data in facility_clauses:
        # 检查是否已存在
        existing = db.query(FacilityScoreDetail).filter(
            FacilityScoreDetail.facility_id == facility_id,
            FacilityScoreDetail.clause_id == clause_data["clause_number"]
        ).first()
        
        if not existing:
            item = FacilityScoreDetail(
                facility_id=facility_id,
                clause_id=clause_data["clause_number"],
                max_score=Decimal(str(clause_data["max_score"])),
                applicable_score=Decimal(str(clause_data["max_score"])),
                actual_score=Decimal("0"),
                is_applicable=True
            )
            db.add(item)
            created_items.append({
                "clause_id": clause_data["clause_number"],
                "description": clause_data["description"],
                "max_score": clause_data["max_score"]
            })
    
    db.commit()
    return {
        "message": f"已生成 {len(created_items)} 条设施评分项",
        "items": created_items
    }

@router.get("/facility-categories")
def list_facility_categories(db: Session = Depends(get_db)):
    """获取所有设施类别（含章节归属，供前端按建筑类型过滤）"""
    from app.models.models import FacilityCategory
    categories = db.query(FacilityCategory).order_by(FacilityCategory.sort_order).all()
    return [
        {
            "id": c.id,
            "category_code": c.category_code,
            "category_name": c.category_name,
            "chapter": c.chapter.value,
            "max_score": float(c.max_score) if c.max_score else 10
        }
        for c in categories
    ]

@router.get("/facility-clauses/{category_code}")
def get_facility_clauses(category_code: str):
    """获取设施类别的标准评分项模板"""
    from app.data.standard_data import FACILITY_CLAUSES
    
    clauses = FACILITY_CLAUSES.get(category_code, [])
    return {
        "category": category_code,
        "count": len(clauses),
        "items": clauses
    }