from enum import Enum

class BuildingType(str, Enum):
    RESIDENTIAL = "residential"              # 住宅类居住建筑
    NON_RESIDENTIAL = "non_residential"      # 非住宅类居住建筑（宿舍、公寓）
    PUBLIC_WITH_ACCOM = "public_with_accom"  # 含住宿功能的公共建筑
    PUBLIC_NO_ACCOM = "public_no_accom"      # 不含住宿功能的公共建筑

class EvaluationType(str, Enum):
    INITIAL = "initial"      # 初评
    RENEWAL = "renewal"      # 复评
    PRE = "pre"              # 预评价

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"

class Chapter(str, Enum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"
    Q5 = "Q5"
    CONSTRUCTION = "construction"
    MAINTENANCE = "maintenance"
    CONTROL = "control"

class ClauseType(str, Enum):
    SYSTEM = "system"
    FACILITY = "facility"
    CONTROL = "control"
    BONUS = "bonus"

class ScoreType(str, Enum):
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE = "multiple"
    CALCULATED = "calculated"

class Grade(str, Enum):
    NONE = "none"
    ONE_STAR = "one_star"
    TWO_STAR = "two_star"
    THREE_STAR = "three_star"

class FacilityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class BuildingStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"