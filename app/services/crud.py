from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.models import *
from app.schemas.schemas import *
from app.core.enums import *
from decimal import Decimal

# ========== 项目CRUD ==========
class ProjectService:
    @staticmethod
    def create(db: Session, obj_in: ProjectCreate) -> Project:
        db_obj = Project(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(Project).order_by(Project.created_at.desc(), Project.id.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, db_obj: Project, obj_in: ProjectUpdate) -> Project:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# ========== 建筑CRUD ==========
class BuildingService:
    @staticmethod
    def create(db: Session, obj_in: BuildingCreate) -> Building:
        db_obj = Building(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, building_id: str) -> Optional[Building]:
        return db.query(Building).filter(Building.id == building_id).first()
    
    @staticmethod
    def get_by_project(db: Session, project_id: str) -> List[Building]:
        return db.query(Building).filter(Building.project_id == project_id).all()
    
    @staticmethod
    def update(db: Session, db_obj: Building, obj_in: BuildingUpdate) -> Building:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Building) -> None:
        """删除建筑及其关联的控制项、系统评分、设施（含设施评分）、评价结果"""
        for facility in db.query(FacilityEntity).filter(FacilityEntity.building_id == db_obj.id).all():
            db.query(FacilityScoreDetail).filter(FacilityScoreDetail.facility_id == facility.id).delete()
            db.delete(facility)
        db.query(ControlItemCheck).filter(ControlItemCheck.building_id == db_obj.id).delete()
        db.query(SystemScoreDetail).filter(SystemScoreDetail.building_id == db_obj.id).delete()
        db.query(DimensionScore).filter(DimensionScore.building_id == db_obj.id).delete()
        db.delete(db_obj)
        db.commit()

# ========== 控制项CRUD ==========
class ControlItemService:
    @staticmethod
    def create(db: Session, building_id: str, obj_in: ControlItemCheckCreate) -> ControlItemCheck:
        db_obj = ControlItemCheck(building_id=building_id, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_by_building(db: Session, building_id: str) -> List[ControlItemCheck]:
        return db.query(ControlItemCheck).filter(ControlItemCheck.building_id == building_id).all()
    
    @staticmethod
    def update(db: Session, db_obj: ControlItemCheck, obj_in: ControlItemCheckUpdate) -> ControlItemCheck:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_by_building_and_chapter(db: Session, building_id: str, chapter: Chapter) -> List[ControlItemCheck]:
        return db.query(ControlItemCheck).filter(
            and_(ControlItemCheck.building_id == building_id, ControlItemCheck.chapter == chapter)
        ).all()

# ========== 系统评分CRUD ==========
class SystemScoreService:
    @staticmethod
    def create(db: Session, building_id: str, obj_in: SystemScoreDetailCreate) -> SystemScoreDetail:
        # 手动创建即视为已评分
        db_obj = SystemScoreDetail(building_id=building_id, is_scored=True, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_by_building(db: Session, building_id: str) -> List[SystemScoreDetail]:
        return db.query(SystemScoreDetail).filter(SystemScoreDetail.building_id == building_id).all()
    
    @staticmethod
    def get_by_building_and_chapter(db: Session, building_id: str, chapter: Chapter) -> List[SystemScoreDetail]:
        return db.query(SystemScoreDetail).filter(
            and_(SystemScoreDetail.building_id == building_id, SystemScoreDetail.chapter == chapter)
        ).all()
    
    @staticmethod
    def update(db: Session, db_obj: SystemScoreDetail, obj_in: ScoreItemUpdate) -> SystemScoreDetail:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

# ========== 设施CRUD ==========
class FacilityService:
    @staticmethod
    def create(db: Session, building_id: str, obj_in: FacilityEntityCreate) -> FacilityEntity:
        db_obj = FacilityEntity(building_id=building_id, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, facility_id: str) -> Optional[FacilityEntity]:
        return db.query(FacilityEntity).filter(FacilityEntity.id == facility_id).first()
    
    @staticmethod
    def get_by_building(db: Session, building_id: str) -> List[FacilityEntity]:
        return db.query(FacilityEntity).options(
            joinedload(FacilityEntity.category),
            joinedload(FacilityEntity.score_items)
        ).filter(FacilityEntity.building_id == building_id).all()
    
    @staticmethod
    def create_score_item(db: Session, facility_id: str, obj_in: FacilityScoreItemCreate) -> FacilityScoreDetail:
        # 手动创建即视为已评分
        db_obj = FacilityScoreDetail(facility_id=facility_id, is_scored=True, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_score_items(db: Session, facility_id: str) -> List[FacilityScoreDetail]:
        return db.query(FacilityScoreDetail).filter(FacilityScoreDetail.facility_id == facility_id).all()

# ========== 标准条文CRUD ==========
class StandardClauseService:
    @staticmethod
    def create(db: Session, obj_in: StandardClauseCreate) -> StandardClause:
        db_obj = StandardClause(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get(db: Session, clause_id: str) -> Optional[StandardClause]:
        return db.query(StandardClause).filter(StandardClause.id == clause_id).first()
    
    @staticmethod
    def get_by_chapter(db: Session, chapter: Chapter) -> List[StandardClause]:
        return db.query(StandardClause).filter(
            and_(StandardClause.chapter == chapter, StandardClause.is_active == True)
        ).order_by(StandardClause.sort_order).all()
    
    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[StandardClause]:
        return db.query(StandardClause).offset(skip).limit(limit).all()

# ========== 评分结果CRUD ==========
class DimensionScoreService:
    @staticmethod
    def create(db: Session, building_id: str, scores: dict) -> DimensionScore:
        db_obj = DimensionScore(building_id=building_id, **scores)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_latest(db: Session, building_id: str) -> Optional[DimensionScore]:
        return db.query(DimensionScore).filter(
            DimensionScore.building_id == building_id
        ).order_by(DimensionScore.calculated_at.desc(), DimensionScore.id.desc()).first()
    
    @staticmethod
    def get_by_building(db: Session, building_id: str) -> List[DimensionScore]:
        return db.query(DimensionScore).filter(
            DimensionScore.building_id == building_id
        ).order_by(DimensionScore.calculated_at.desc()).all()

# ========== 建筑群评分CRUD ==========
class ComplexScoreService:
    @staticmethod
    def create(db: Session, project_id: str, z1: Decimal, z2: Decimal, zq: Decimal, building_scores: dict,
               dimension_scores: dict = None, determined_grade=None, breakdown: dict = None) -> ComplexBuildingScore:
        db_obj = ComplexBuildingScore(
            project_id=project_id,
            z1_score=z1,
            z2_score=z2,
            zq_score=zq,
            building_scores=building_scores,
            dimension_scores=dimension_scores,
            determined_grade=determined_grade,
            breakdown=breakdown,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    @staticmethod
    def get_by_project(db: Session, project_id: str) -> Optional[ComplexBuildingScore]:
        return db.query(ComplexBuildingScore).filter(
            ComplexBuildingScore.project_id == project_id
        ).order_by(ComplexBuildingScore.calculated_at.desc()).first()