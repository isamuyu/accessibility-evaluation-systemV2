from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.models import StandardClause, FacilityCategory, BuildingTypeRule
from app.core.enums import *
from decimal import Decimal
from app.data.standard_data import STANDARD_CLAUSES, FACILITY_CLAUSES
import json
import os

def init_standard_clauses(db: Session):
    """初始化标准条文数据（幂等：按条文编号 upsert，保持 id 稳定）"""
    inserted = updated = 0
    for data in STANDARD_CLAUSES:
        existing = db.query(StandardClause).filter(
            StandardClause.clause_number == data["clause_number"]
        ).first()
        if existing:
            existing.chapter = Chapter(data["chapter"])
            existing.clause_type = ClauseType(data["clause_type"])
            existing.description = data["description"]
            existing.score_type = ScoreType(data["score_type"])
            existing.applicable_building_types = data["applicable"]
            existing.options = data.get("options")
            existing.parent_clause = data["parent"]
            existing.max_score = Decimal(str(data["max_score"]))
            existing.sort_order = data.get("sort_order", 0)
            existing.is_active = True
            updated += 1
        else:
            clause = StandardClause(
                clause_number=data["clause_number"],
                chapter=Chapter(data["chapter"]),
                clause_type=ClauseType(data["clause_type"]),
                description=data["description"],
                score_type=ScoreType(data["score_type"]),
                applicable_building_types=data["applicable"],
                options=data.get("options"),
                parent_clause=data["parent"],
                max_score=Decimal(str(data["max_score"])),
                sort_order=data.get("sort_order", 0),
                is_active=True,
                version="2022"
            )
            db.add(clause)
            inserted += 1

    db.commit()
    print(f"标准条文：新增 {inserted} 条，更新 {updated} 条")

def init_facility_categories(db: Session):
    """初始化设施类别"""
    categories = [
        FacilityCategory(category_code="通道", category_name="无障碍通道", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="坡道", category_name="轮椅坡道", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="出入口", category_name="无障碍出入口", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="门", category_name="门", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="电梯", category_name="无障碍电梯", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="盲道", category_name="盲道", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="其他通行设施", category_name="其他无障碍通行设施", chapter=Chapter.Q1, max_score=Decimal("10")),
        FacilityCategory(category_code="公共卫生间", category_name="满足无障碍要求的公共卫生间", chapter=Chapter.Q2, max_score=Decimal("10")),
        FacilityCategory(category_code="无障碍厕所", category_name="无障碍厕所", chapter=Chapter.Q2, max_score=Decimal("10")),
        FacilityCategory(category_code="公共浴室", category_name="公共浴室和更衣室", chapter=Chapter.Q2, max_score=Decimal("10")),
        FacilityCategory(category_code="轮椅席位", category_name="轮椅席位和低位服务设施", chapter=Chapter.Q2, max_score=Decimal("10")),
        FacilityCategory(category_code="居室", category_name="居室", chapter=Chapter.Q3, max_score=Decimal("10")),
        FacilityCategory(category_code="无障碍卫生间", category_name="无障碍卫生间", chapter=Chapter.Q3, max_score=Decimal("10")),
    ]
    
    inserted = 0
    for cat in categories:
        existing = db.query(FacilityCategory).filter(
            FacilityCategory.category_code == cat.category_code
        ).first()
        if existing:
            existing.category_name = cat.category_name
            existing.chapter = cat.chapter
            existing.max_score = cat.max_score
            existing.sort_order = cat.sort_order
        else:
            db.add(cat)
            inserted += 1

    db.commit()
    print(f"设施类别：新增 {inserted} 个，共 {len(categories)} 个")

def init_building_type_rules(db: Session):
    """初始化建筑类型规则（由评分策略派生，保证单一数据源）"""
    from app.services.scoring_engine import StrategyFactory

    rules = []
    for bt in BuildingType:
        strategy = StrategyFactory.get_strategy(bt)
        chapters = [c.value for c in strategy.get_applicable_chapters()]
        base_chapters = [c for c in chapters if c != "Q5"]
        rules.append(BuildingTypeRule(
            building_type=bt,
            applicable_chapters=chapters,
            total_formula=f"({'+'.join(base_chapters)})/{strategy.get_divisor()}+Q5",
            divisor=strategy.get_divisor(),
            required_facility_categories=strategy.get_required_facility_categories()
        ))
    
    inserted = 0
    for rule in rules:
        existing = db.query(BuildingTypeRule).filter(
            BuildingTypeRule.building_type == rule.building_type
        ).first()
        if existing:
            existing.applicable_chapters = rule.applicable_chapters
            existing.total_formula = rule.total_formula
            existing.divisor = rule.divisor
            existing.required_facility_categories = rule.required_facility_categories
            existing.is_active = True
        else:
            db.add(rule)
            inserted += 1

    db.commit()
    print(f"建筑类型规则：新增 {inserted} 条，共 {len(rules)} 条")

def init_facility_mode(db: Session):
    """初始化设施评价模式数据（幂等：按编码 upsert）"""
    from app.models.models import FacilityModeCategory, FacilityModeClause

    data_path = os.path.join(os.path.dirname(__file__), "app", "data", "facility_mode_data.json")
    data = json.load(open(data_path, encoding="utf-8"))

    cat_inserted = 0
    for order, cat in enumerate(data["categories"]):
        existing = db.query(FacilityModeCategory).filter(
            FacilityModeCategory.category_code == cat["category_code"]).first()
        if existing:
            existing.category_name = cat["category_name"]
            existing.facility_category_code = cat.get("facility_category_code")
            existing.sort_order = order
        else:
            db.add(FacilityModeCategory(
                category_code=cat["category_code"],
                category_name=cat["category_name"],
                facility_category_code=cat.get("facility_category_code"),
                sort_order=order,
            ))
            cat_inserted += 1

    clause_inserted = updated = 0
    for c in data["clauses"]:
        existing = db.query(FacilityModeClause).filter(
            FacilityModeClause.clause_number == c["clause_number"]).first()
        if existing:
            for k in ("standard_clause_number", "category_code", "chapter", "clause_type",
                      "title", "content", "max_score", "score_type", "score_options", "sort_order"):
                setattr(existing, k, c[k])
            updated += 1
        else:
            db.add(FacilityModeClause(**c))
            clause_inserted += 1

    db.commit()
    print(f"设施模式类别：新增 {cat_inserted}，共 {len(data['categories'])}；条款：新增 {clause_inserted}，更新 {updated}")


def init_admin_user(db: Session):
    """默认管理员账号（生产环境请登录后立即修改密码）"""
    from app.models.models import User
    from app.core.security import get_password_hash
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123"), full_name="管理员"))
        db.commit()
        print("已创建默认管理员: admin / admin123")
    else:
        print("管理员账号已存在")


def main():
    print("开始初始化数据库...")
    
    # 先创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    db = SessionLocal()
    try:
        init_standard_clauses(db)
        init_facility_categories(db)
        init_building_type_rules(db)
        init_facility_mode(db)
        init_admin_user(db)

        print("数据库初始化完成！")
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()