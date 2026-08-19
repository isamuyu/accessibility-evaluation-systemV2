import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.core.database import Base, get_db
from app.models.models import FacilityCategory, StandardClause
from app.core.enums import Chapter, ClauseType, ScoreType

# 真正的内存数据库（StaticPool 保证跨线程共享同一连接）
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    # 认证已默认开启：每个测试用例内注册并登录，给共享 client 带上令牌
    client.post("/auth/register", json={"username": "testadmin", "password": "test123456"})
    token = client.post("/auth/login", json={"username": "testadmin", "password": "test123456"}).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield
    Base.metadata.drop_all(bind=engine)


def seed_facility_categories():
    """写入设施类别种子数据（幂等），返回 {category_code: id}"""
    db = TestingSessionLocal()
    try:
        for code, chapter in [("通道", Chapter.Q1), ("公共卫生间", Chapter.Q2), ("居室", Chapter.Q3)]:
            if not db.query(FacilityCategory).filter(FacilityCategory.category_code == code).first():
                db.add(FacilityCategory(category_code=code, category_name=code, chapter=chapter, max_score=Decimal("10")))
        db.commit()
        return {c.category_code: c.id for c in db.query(FacilityCategory).all()}
    finally:
        db.close()


def create_project_and_building(building_type="public_no_accom"):
    project_resp = client.post("/projects/", json={
        "project_name": "测试项目", "evaluation_type": "initial"
    })
    project_id = project_resp.json()["id"]
    building_resp = client.post("/buildings/", json={
        "project_id": project_id,
        "building_name": "测试楼",
        "building_type": building_type,
        "floor_area": "20000.00",
        "is_within_one_year": True
    })
    return project_id, building_resp.json()["id"]


def seed_standard_clause(clause_number, chapter, clause_type, applicable, parent=None, max_score=0):
    db = TestingSessionLocal()
    try:
        clause = StandardClause(
            clause_number=clause_number,
            chapter=Chapter(chapter),
            clause_type=ClauseType(clause_type),
            description=f"测试条文 {clause_number}",
            score_type=ScoreType("boolean" if clause_type == "control" else "single_choice"),
            applicable_building_types=applicable,
            parent_clause=parent,
            max_score=Decimal(str(max_score)),
            is_active=True,
        )
        db.add(clause)
        db.commit()
        return clause.id
    finally:
        db.close()
