import pytest
from decimal import Decimal
from tests.conftest import (
    client, setup_db, seed_facility_categories, create_project_and_building,
    TestingSessionLocal, engine
)
from app.core.database import Base
from app.models.models import (
    FacilityModeCategory, FacilityModeClause, StandardClause, FacilityCategory
)
from app.core.enums import Chapter
from tests.conftest import seed_standard_clause


def seed_facility_mode():
    """写入设施模式测试数据：坡道类别（设施条款）+ 流线类别（系统/控制条款）"""
    db = TestingSessionLocal()
    cat1 = FacilityModeCategory(category_code="wheelchair_ramp", category_name="轮椅坡道",
                                facility_category_code="坡道", sort_order=1)
    cat2 = FacilityModeCategory(category_code="accessible_circulation", category_name="无障碍流线",
                                facility_category_code=None, sort_order=2)
    db.add_all([cat1, cat2])
    # 坡道类别也需 FacilityCategory
    if not db.query(FacilityCategory).filter(FacilityCategory.category_code == "坡道").first():
        db.add(FacilityCategory(category_code="坡道", category_name="轮椅坡道",
                                chapter=Chapter.Q1, max_score=Decimal("10")))
    clauses = [
        # 设施条款：5.3.2.1（布尔，满分1）
        FacilityModeClause(clause_number="wheelchair_ramp-5.3.2.1", standard_clause_number="5.3.2.1",
                           category_code="wheelchair_ramp", chapter=Chapter.Q1, clause_type="facility",
                           title="坡道形式", content="直线形", max_score=Decimal("1"), score_type="boolean"),
        # 设施条款：5.3.2.2（布尔，满分2）
        FacilityModeClause(clause_number="wheelchair_ramp-5.3.2.2", standard_clause_number="5.3.2.2",
                           category_code="wheelchair_ramp", chapter=Chapter.Q1, clause_type="facility",
                           title="井盖篦子", content="上下坡无井盖", max_score=Decimal("2"), score_type="boolean"),
        # 系统条款：5.2.1.2（单选，满分8）
        FacilityModeClause(clause_number="accessible_circulation-5.2.1.2", standard_clause_number="5.2.1.2",
                           category_code="accessible_circulation", chapter=Chapter.Q1, clause_type="system",
                           title="流线一致性", content="一致8分", max_score=Decimal("8"), score_type="single_choice",
                           score_options={"options": [{"label": "一致", "score": 8}, {"label": "无绕行", "score": 6}]}),
        # 控制条款：5.1.1.1
        FacilityModeClause(clause_number="accessible_circulation-5.1.1.1", standard_clause_number="5.1.1.1",
                           category_code="accessible_circulation", chapter=Chapter.Q1, clause_type="control",
                           title="流线连贯", content="无障碍流线连贯", max_score=Decimal("0"), score_type="boolean"),
    ]
    db.add_all(clauses)
    db.commit()
    ids = {c.clause_number: c.id for c in db.query(FacilityModeClause).all()}
    db.close()
    return ids


class TestFacilityMode:
    """设施评价模式：实例→核查→自动映射"""

    def test_full_flow(self, setup_db):
        clause_ids = seed_facility_mode()
        category_ids = seed_facility_categories()
        # 系统/控制条款映射目标
        seed_standard_clause("5.2.1.2", "Q1", "system", ["residential"], max_score=8)
        seed_standard_clause("5.1.1.1", "control", "control", ["residential"], parent="Q1")

        _, building_id = create_project_and_building("residential")

        # 1. 类别列表（住宅参评Q1/Q3/Q4/Q5，两类都有Q1条款）
        resp = client.get(f"/facility-mode/categories/{building_id}")
        assert resp.status_code == 200
        codes = [c["category_code"] for c in resp.json()["categories"]]
        assert "wheelchair_ramp" in codes and "accessible_circulation" in codes

        # 2. 建坡道实例并核查（设施条款）
        inst = client.post("/facility-mode/instances", json={
            "building_id": building_id, "category_code": "wheelchair_ramp",
            "instance_name": "1#坡道", "location": "南门"
        }).json()
        checks = client.get(f"/facility-mode/instances/{inst['id']}/clauses").json()["clauses"]
        assert len(checks) == 2

        resp = client.post(f"/facility-mode/instances/{inst['id']}/checks", json={"checks": [
            {"clause_id": clause_ids["wheelchair_ramp-5.3.2.1"], "status": "passed",
             "selected_option": {"status": "passed"}},
            {"clause_id": clause_ids["wheelchair_ramp-5.3.2.2"], "status": "failed",
             "selected_option": {"status": "failed"}},
        ]})
        assert resp.status_code == 200
        assert resp.json()["mapped"]["facility_scores"] == 2

        # 验证：自动创建了设施实体 + 设施评分（5.3.2.1=1分，5.3.2.2=0分）
        facilities = client.get(f"/scoring/facilities/{building_id}").json()
        assert len(facilities) == 1
        items = client.get(f"/scoring/facilities/{facilities[0]['id']}/scores").json()
        by_clause = {i["clause_id"]: i for i in items}
        assert Decimal(by_clause["5.3.2.1"]["actual_score"]) == Decimal("1")
        assert Decimal(by_clause["5.3.2.2"]["actual_score"]) == Decimal("0")
        assert by_clause["5.3.2.1"]["is_scored"] is True

        # 3. 流线实例：系统条款选"无绕行"(6分)，控制条款达标
        inst2 = client.post("/facility-mode/instances", json={
            "building_id": building_id, "category_code": "accessible_circulation",
            "instance_name": "主流线"}).json()
        resp = client.post(f"/facility-mode/instances/{inst2['id']}/checks", json={"checks": [
            {"clause_id": clause_ids["accessible_circulation-5.2.1.2"], "status": "passed",
             "selected_option": {"status": "passed", "optionIndex": 1}},
            {"clause_id": clause_ids["accessible_circulation-5.1.1.1"], "status": "passed",
             "selected_option": {"status": "passed"}},
        ]})
        assert resp.json()["mapped"]["score_items"] == 1
        assert resp.json()["mapped"]["control_checks"] == 1

        # 验证系统评分和控制项
        scores = client.get(f"/scoring/system-scores/{building_id}").json()
        s12 = next(s for s in scores if s["clause_number"] == "5.2.1.2")
        assert Decimal(s12["actual_score"]) == Decimal("6")
        controls = client.get(f"/scoring/control-items/{building_id}").json()
        assert controls[0]["is_compliant"] is True

    def test_progress(self, setup_db):
        clause_ids = seed_facility_mode()
        seed_facility_categories()
        _, building_id = create_project_and_building("residential")
        inst = client.post("/facility-mode/instances", json={
            "building_id": building_id, "category_code": "wheelchair_ramp",
            "instance_name": "1#坡道"}).json()
        client.post(f"/facility-mode/instances/{inst['id']}/checks", json={"checks": [
            {"clause_id": clause_ids["wheelchair_ramp-5.3.2.1"], "status": "passed",
             "selected_option": {"status": "passed"}},
        ]})
        prog = client.get(f"/facility-mode/progress/{building_id}").json()
        assert prog["total"] == 2 and prog["checked"] == 1 and prog["progress"] == 50.0

    def test_na_control_not_mapped(self, setup_db):
        """控制项不参评时不写入（不卡闸门）"""
        clause_ids = seed_facility_mode()
        seed_facility_categories()
        seed_standard_clause("5.1.1.1", "control", "control", ["residential"], parent="Q1")
        _, building_id = create_project_and_building("residential")
        inst = client.post("/facility-mode/instances", json={
            "building_id": building_id, "category_code": "accessible_circulation",
            "instance_name": "流线1"}).json()
        resp = client.post(f"/facility-mode/instances/{inst['id']}/checks", json={"checks": [
            {"clause_id": clause_ids["accessible_circulation-5.1.1.1"], "status": "na",
             "selected_option": {"status": "na"}},
        ]})
        assert resp.json()["mapped"]["control_checks"] == 0
        assert client.get(f"/scoring/control-items/{building_id}").json() == []
