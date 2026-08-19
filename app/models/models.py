import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, DECIMAL, Integer, ForeignKey, Text, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship


def _utcnow():
    """UTC 当前时间（naive，与既有数据库数据保持一致）"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
from app.core.database import Base
from app.core.enums import (
    BuildingType, EvaluationType, ProjectStatus, Chapter, 
    ClauseType, ScoreType, Grade, FacilityStatus, BuildingStatus
)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String(200), nullable=False)
    project_code = Column(String(50), unique=True)
    applicant_name = Column(String(200))
    applicant_contact = Column(String(100))
    evaluation_type = Column(SQLEnum(EvaluationType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    standard_version = Column(String(10), default="2022")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    
    buildings = relationship("Building", back_populates="project")
    complex_score = relationship("ComplexBuildingScore", back_populates="project", uselist=False)

class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    building_name = Column(String(200), nullable=False)
    building_code = Column(String(50))
    building_type = Column(SQLEnum(BuildingType), nullable=False)
    floor_area = Column(DECIMAL(10, 2))
    completion_date = Column(DateTime)
    is_within_one_year = Column(Boolean, default=True)
    # 竣工一年后评价须按GB50642现场检测合格（表3）
    site_inspection_passed = Column(Boolean)
    status = Column(SQLEnum(BuildingStatus), default=BuildingStatus.ACTIVE)
    
    project = relationship("Project", back_populates="buildings")
    control_items = relationship("ControlItemCheck", back_populates="building")
    system_scores = relationship("SystemScoreDetail", back_populates="building")
    facilities = relationship("FacilityEntity", back_populates="building")
    dimension_scores = relationship("DimensionScore", back_populates="building")

class StandardClause(Base):
    __tablename__ = "standard_clauses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clause_number = Column(String(20), nullable=False, unique=True)
    chapter = Column(SQLEnum(Chapter), nullable=False)
    clause_type = Column(SQLEnum(ClauseType), nullable=False)
    description = Column(Text, nullable=False)
    max_score = Column(DECIMAL(5, 2), default=0)
    score_type = Column(SQLEnum(ScoreType), nullable=False)
    applicable_building_types = Column(JSON)
    # 单选评分档（single_choice类条文）：[{"label": "...", "score": 8}, ...]
    options = Column(JSON)
    parent_clause = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    version = Column(String(10), default="2022")
    created_at = Column(DateTime, default=_utcnow)

class FacilityCategory(Base):
    __tablename__ = "facility_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_code = Column(String(20), nullable=False, unique=True)
    category_name = Column(String(100), nullable=False)
    chapter = Column(SQLEnum(Chapter), nullable=False)
    max_score = Column(DECIMAL(5, 2), default=10)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    
    facilities = relationship("FacilityEntity", back_populates="category")

class BuildingTypeRule(Base):
    __tablename__ = "building_type_rules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_type = Column(SQLEnum(BuildingType), nullable=False)
    applicable_chapters = Column(JSON, nullable=False)
    total_formula = Column(String(100), nullable=False)
    divisor = Column(Integer, nullable=False)
    required_facility_categories = Column(JSON)
    is_active = Column(Boolean, default=True)

class ControlItemCheck(Base):
    __tablename__ = "control_item_checks"
    __table_args__ = (
        UniqueConstraint("building_id", "clause_id", name="uq_control_item_building_clause"),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    clause_id = Column(String(36), ForeignKey("standard_clauses.id"), nullable=False)
    chapter = Column(SQLEnum(Chapter), nullable=False)
    is_compliant = Column(Boolean)
    check_result = Column(Text)
    evidence_photos = Column(JSON)
    checked_by = Column(String(50))
    checked_at = Column(DateTime)
    
    building = relationship("Building", back_populates="control_items")

class SystemScoreDetail(Base):
    __tablename__ = "system_score_details"
    __table_args__ = (
        UniqueConstraint("building_id", "clause_id", name="uq_system_score_building_clause"),
    )
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    clause_id = Column(String(36), ForeignKey("standard_clauses.id"), nullable=False)
    chapter = Column(SQLEnum(Chapter), nullable=False)
    max_score = Column(DECIMAL(5, 2), nullable=False)
    applicable_score = Column(DECIMAL(5, 2), nullable=False)
    actual_score = Column(DECIMAL(5, 2), nullable=False)
    is_applicable = Column(Boolean, default=True)
    # 是否已评分（区分"未评分"与"评了0分"）
    is_scored = Column(Boolean, default=False)
    not_applicable_reason = Column(Text)
    evidence_photos = Column(JSON)
    scored_by = Column(String(50))
    scored_at = Column(DateTime)

    building = relationship("Building", back_populates="system_scores")

class FacilityEntity(Base):
    __tablename__ = "facility_entities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("facility_categories.id"), nullable=False)
    facility_name = Column(String(200))
    location_description = Column(Text)
    floor_number = Column(String(20))
    area_name = Column(String(100))
    status = Column(SQLEnum(FacilityStatus), default=FacilityStatus.ACTIVE)
    created_at = Column(DateTime, default=_utcnow)
    
    building = relationship("Building", back_populates="facilities")
    category = relationship("FacilityCategory", back_populates="facilities")
    score_items = relationship("FacilityScoreDetail", back_populates="facility")

class FacilityScoreDetail(Base):
    __tablename__ = "facility_score_details"
    __table_args__ = (
        UniqueConstraint("facility_id", "clause_id", name="uq_facility_score_facility_clause"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id = Column(String(36), ForeignKey("facility_entities.id"), nullable=False)
    # 存储设施评分条文编号（如 "5.3.1.1a"），对应 FACILITY_CLAUSES 模板，非 standard_clauses 外键
    clause_id = Column(String(36), nullable=False)
    max_score = Column(DECIMAL(5, 2), nullable=False)
    applicable_score = Column(DECIMAL(5, 2), nullable=False)
    actual_score = Column(DECIMAL(5, 2), nullable=False)
    is_applicable = Column(Boolean, default=True)
    # 是否已评分（区分"未评分"与"评了0分"）
    is_scored = Column(Boolean, default=False)
    not_applicable_reason = Column(Text)
    evidence_photos = Column(JSON)
    scored_by = Column(String(50))
    scored_at = Column(DateTime)

    facility = relationship("FacilityEntity", back_populates="score_items")

class DimensionScore(Base):
    __tablename__ = "dimension_scores"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    calculation_version = Column(Integer, default=1)
    
    q1_system_score = Column(DECIMAL(5, 2))
    q1_facility_score = Column(DECIMAL(5, 2))
    q1_score = Column(DECIMAL(5, 2))
    
    q2_system_score = Column(DECIMAL(5, 2))
    q2_facility_score = Column(DECIMAL(5, 2))
    q2_score = Column(DECIMAL(5, 2))
    
    q3_system_score = Column(DECIMAL(5, 2))
    q3_facility_score = Column(DECIMAL(5, 2))
    q3_score = Column(DECIMAL(5, 2))
    
    q4_score = Column(DECIMAL(5, 2))
    q5_score = Column(DECIMAL(5, 2))
    
    construction_score = Column(DECIMAL(5, 2))
    maintenance_score = Column(DECIMAL(5, 2))
    
    total_score_q = Column(DECIMAL(5, 2))
    determined_grade = Column(SQLEnum(Grade))
    # 评级依据明细（含未达标原因）
    breakdown = Column(JSON)
    grade_determined_at = Column(DateTime)
    grade_determined_by = Column(String(50))
    
    source_data_hash = Column(String(64))
    calculated_at = Column(DateTime, default=_utcnow)
    
    building = relationship("Building", back_populates="dimension_scores")

class FacilityCategoryAverage(Base):
    __tablename__ = "facility_category_averages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dimension_score_id = Column(String(36), ForeignKey("dimension_scores.id"), nullable=False)
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("facility_categories.id"), nullable=False)
    facility_count = Column(Integer)
    category_average = Column(DECIMAL(5, 2))
    calculated_at = Column(DateTime, default=_utcnow)

# ========== 设施评价模式（新手快速录入，自动映射到Q维度） ==========

class FacilityModeCategory(Base):
    """设施模式类别（比设施类别更细，如门分主入口/厕所门）"""
    __tablename__ = "facility_mode_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_code = Column(String(30), unique=True, nullable=False)
    category_name = Column(String(100), nullable=False)
    # 归并到的设施类别编码（FacilityCategory.category_code），None表示无对应设施（纯系统/控制项类别）
    facility_category_code = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    clauses = relationship("FacilityModeClause", back_populates="category")


class FacilityModeClause(Base):
    """设施模式条款（含选项，standard_clause_number 回链标准条款）"""
    __tablename__ = "facility_mode_clauses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clause_number = Column(String(80), unique=True, nullable=False)  # 类别编码-标准编号
    standard_clause_number = Column(String(50))  # 如 5.3.1.1 / 5.3.6.2d
    category_code = Column(String(30), ForeignKey("facility_mode_categories.category_code"), nullable=False)
    chapter = Column(SQLEnum(Chapter), nullable=False)
    clause_type = Column(String(20), nullable=False)  # control/system/facility
    title = Column(String(200))
    content = Column(Text)
    max_score = Column(DECIMAL(5, 2), default=0)
    score_type = Column(String(20), nullable=False)  # boolean/single_choice/multiple
    score_options = Column(JSON)  # {options:[...]} 或 {sub_items:[...]}
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    category = relationship("FacilityModeCategory", back_populates="clauses")


class FacilityModeInstance(Base):
    """设施模式实例（某建筑下的具体设施，如 1#坡道）"""
    __tablename__ = "facility_mode_instances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=False)
    category_code = Column(String(30), ForeignKey("facility_mode_categories.category_code"), nullable=False)
    instance_name = Column(String(200), nullable=False)
    location = Column(Text)
    sort_order = Column(Integer, default=0)
    # 自动映射时创建/关联的设施实体
    mapped_facility_id = Column(String(36), ForeignKey("facility_entities.id"))
    created_at = Column(DateTime, default=_utcnow)

    checks = relationship("FacilityModeCheck", back_populates="instance", cascade="all, delete-orphan")


class FacilityModeCheck(Base):
    """设施模式核查记录（用户选择）"""
    __tablename__ = "facility_mode_checks"
    __table_args__ = (
        UniqueConstraint("instance_id", "clause_id", name="uq_fm_check_instance_clause"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instance_id = Column(String(36), ForeignKey("facility_mode_instances.id"), nullable=False)
    clause_id = Column(String(36), ForeignKey("facility_mode_clauses.id"), nullable=False)
    status = Column(String(10), default="pending")  # passed/failed/na/pending
    selected_option = Column(JSON)  # {status} / {optionIndex} / {subItems:[{subIndex, checked}]}
    auto_score = Column(DECIMAL(5, 2), default=0)
    notes = Column(Text)
    checked_at = Column(DateTime)

    instance = relationship("FacilityModeInstance", back_populates="checks")
    clause = relationship("FacilityModeClause")


class ComplexBuildingScore(Base):
    __tablename__ = "complex_building_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    z1_score = Column(DECIMAL(5, 2))
    z2_score = Column(DECIMAL(5, 2))
    zq_score = Column(DECIMAL(5, 2))
    # 面积加权的各维度综合分值 {"q1": ..., "q2": ..., "construction": ..., ...}
    dimension_scores = Column(JSON)
    determined_grade = Column(SQLEnum(Grade))
    breakdown = Column(JSON)
    building_scores = Column(JSON)
    calculated_at = Column(DateTime, default=_utcnow)
    
    project = relationship("Project", back_populates="complex_score")