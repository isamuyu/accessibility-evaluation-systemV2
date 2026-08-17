from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.core.enums import *

# 基础Schema
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}

# ========== 认证相关 ==========
class UserCreate(BaseSchema):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None

class UserLogin(BaseSchema):
    username: str
    password: str

class UserResponse(BaseSchema):
    id: str
    username: str
    full_name: Optional[str]
    is_active: bool

class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"

# ========== 项目相关 ==========
class ProjectCreate(BaseSchema):
    project_name: str
    project_code: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_contact: Optional[str] = None
    evaluation_type: EvaluationType

class ProjectUpdate(BaseSchema):
    project_name: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_contact: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseSchema):
    id: str
    project_name: str
    project_code: Optional[str]
    applicant_name: Optional[str]
    applicant_contact: Optional[str]
    evaluation_type: EvaluationType
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

# ========== 建筑相关 ==========
class BuildingCreate(BaseSchema):
    project_id: str
    building_name: str
    building_code: Optional[str] = None
    building_type: BuildingType
    floor_area: Optional[Decimal] = None
    completion_date: Optional[datetime] = None
    is_within_one_year: bool = True
    site_inspection_passed: Optional[bool] = None

class BuildingUpdate(BaseSchema):
    building_name: Optional[str] = None
    building_code: Optional[str] = None
    floor_area: Optional[Decimal] = None
    completion_date: Optional[datetime] = None
    is_within_one_year: Optional[bool] = None
    site_inspection_passed: Optional[bool] = None

class BuildingResponse(BaseSchema):
    id: str
    project_id: str
    building_name: str
    building_code: Optional[str]
    building_type: BuildingType
    floor_area: Optional[Decimal]
    completion_date: Optional[datetime]
    is_within_one_year: bool
    site_inspection_passed: Optional[bool]
    status: BuildingStatus

# ========== 评分项 ==========
class ScoreItemCreate(BaseSchema):
    clause_id: str
    max_score: Decimal
    applicable_score: Decimal
    actual_score: Decimal
    is_applicable: bool = True
    not_applicable_reason: Optional[str] = None
    evidence_photos: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_scores(self):
        if self.max_score < 0:
            raise ValueError("满分不能为负数")
        if not (Decimal("0") <= self.applicable_score <= self.max_score):
            raise ValueError("参评分值必须在 0 到满分之间")
        if not (Decimal("0") <= self.actual_score <= self.max_score):
            raise ValueError("实际得分必须在 0 到满分之间")
        return self

class ScoreItemUpdate(BaseSchema):
    actual_score: Optional[Decimal] = Field(default=None, ge=0)
    is_applicable: Optional[bool] = None
    not_applicable_reason: Optional[str] = None
    evidence_photos: Optional[List[str]] = None

# ========== 控制项 ==========
class ControlItemCheckCreate(BaseSchema):
    clause_id: str
    chapter: Chapter
    is_compliant: Optional[bool] = None
    check_result: Optional[str] = None
    evidence_photos: Optional[List[str]] = None

class ControlItemCheckUpdate(BaseSchema):
    is_compliant: Optional[bool] = None
    check_result: Optional[str] = None
    evidence_photos: Optional[List[str]] = None

class ControlItemCheckResponse(BaseSchema):
    id: str
    building_id: str
    clause_id: str
    clause_number: Optional[str] = None
    description: Optional[str] = None
    applicable_building_types: Optional[List[str]] = None
    chapter: Chapter
    is_compliant: Optional[bool]
    check_result: Optional[str]
    checked_by: Optional[str]
    checked_at: Optional[datetime]

# ========== 系统评分 ==========
class SystemScoreDetailCreate(ScoreItemCreate):
    chapter: Chapter

class SystemScoreDetailResponse(BaseSchema):
    id: str
    building_id: str
    clause_id: str
    clause_number: Optional[str] = None
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    applicable_building_types: Optional[List[str]] = None
    chapter: Chapter
    max_score: Decimal
    applicable_score: Decimal
    actual_score: Decimal
    is_applicable: bool
    is_scored: bool = False
    scored_by: Optional[str]
    scored_at: Optional[datetime]

# ========== 设施相关 ==========
class FacilityEntityCreate(BaseSchema):
    category_id: str
    facility_name: Optional[str] = None
    location_description: Optional[str] = None
    floor_number: Optional[str] = None
    area_name: Optional[str] = None

class FacilityEntityResponse(BaseSchema):
    id: str
    building_id: str
    category_id: str
    facility_name: Optional[str]
    location_description: Optional[str]
    floor_number: Optional[str]
    area_name: Optional[str]
    status: FacilityStatus

# ========== 设施评分 ==========
class FacilityScoreItemCreate(ScoreItemCreate):
    pass

class FacilityScoreDetailResponse(BaseSchema):
    id: str
    facility_id: str
    clause_id: str
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    max_score: Decimal
    applicable_score: Decimal
    actual_score: Decimal
    is_applicable: bool
    is_scored: bool = False

# ========== 评分结果 ==========
class DimensionScoreResponse(BaseSchema):
    id: str
    building_id: str
    calculation_version: int
    
    q1_system_score: Optional[Decimal]
    q1_facility_score: Optional[Decimal]
    q1_score: Optional[Decimal]
    
    q2_system_score: Optional[Decimal]
    q2_facility_score: Optional[Decimal]
    q2_score: Optional[Decimal]
    
    q3_system_score: Optional[Decimal]
    q3_facility_score: Optional[Decimal]
    q3_score: Optional[Decimal]
    
    q4_score: Optional[Decimal]
    q5_score: Optional[Decimal]
    
    construction_score: Optional[Decimal]
    maintenance_score: Optional[Decimal]
    
    total_score_q: Optional[Decimal]
    determined_grade: Optional[Grade]
    breakdown: Optional[Dict[str, Any]] = None
    calculated_at: datetime

class EvaluationResult(BaseSchema):
    building_id: str
    eligible: bool
    grade: Optional[Grade] = None
    total_score_q: Optional[Decimal] = None
    q1_score: Optional[Decimal] = None
    q2_score: Optional[Decimal] = None
    q3_score: Optional[Decimal] = None
    q4_score: Optional[Decimal] = None
    q5_score: Optional[Decimal] = None
    construction_score: Optional[Decimal] = None
    maintenance_score: Optional[Decimal] = None
    reason: Optional[str] = None
    breakdown: Optional[Dict[str, Any]] = None

# ========== 标准条文 ==========
class StandardClauseCreate(BaseSchema):
    clause_number: str
    chapter: Chapter
    clause_type: ClauseType
    description: str
    max_score: Decimal = Decimal("0")
    score_type: ScoreType
    applicable_building_types: Optional[List[BuildingType]] = None
    parent_clause: Optional[str] = None
    sort_order: int = 0

class StandardClauseResponse(BaseSchema):
    id: str
    clause_number: str
    chapter: Chapter
    clause_type: ClauseType
    description: str
    max_score: Decimal
    score_type: ScoreType
    is_active: bool

# ========== 建筑群评分 ==========
class ComplexBuildingScoreResponse(BaseSchema):
    id: str
    project_id: str
    z1_score: Optional[Decimal]
    z2_score: Optional[Decimal]
    zq_score: Optional[Decimal]
    dimension_scores: Optional[Dict]
    determined_grade: Optional[Grade]
    breakdown: Optional[Dict[str, Any]] = None
    building_scores: Optional[Dict]
    calculated_at: datetime