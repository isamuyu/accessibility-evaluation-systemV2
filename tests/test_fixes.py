import pytest
from decimal import Decimal
from tests.conftest import (
    client, setup_db, seed_facility_categories, create_project_and_building,
    seed_standard_clause
)


def add_compliant_control_items(building_id, chapters=("Q1",)):
    for i, ch in enumerate(chapters):
        resp = client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": f"ctrl-{ch}-{i}", "chapter": ch, "is_compliant": True
        })
        assert resp.status_code == 200


class TestEvaluateGuards:
    """评价前置条件检查"""

    def test_evaluate_without_control_items_rejected(self, setup_db):
        """无控制项记录时应拒绝评价"""
        seed_facility_categories()
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/evaluate/{building_id}")
        assert resp.status_code == 200
        result = resp.json()
        assert result["eligible"] is False
        assert "控制项" in result["reason"]

    def test_evaluate_without_facilities_rejected(self, setup_db):
        """有控制项但无设施数据时应拒绝评价"""
        _, building_id = create_project_and_building()
        add_compliant_control_items(building_id)
        resp = client.post(f"/scoring/evaluate/{building_id}")
        assert resp.status_code == 200
        result = resp.json()
        assert result["eligible"] is False
        assert "设施" in result["reason"]

    def test_evaluate_with_unchecked_control_item_rejected(self, setup_db):
        """控制项未核查（is_compliant=None）时不予通过"""
        seed_facility_categories()
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "ctrl-1", "chapter": "Q1", "is_compliant": None
        })
        assert resp.status_code == 200
        resp = client.post(f"/scoring/evaluate/{building_id}")
        assert resp.json()["eligible"] is False


class TestFacilityScoreByChapter:
    """设施分按章节计入 Q1/Q2/Q3"""

    def _build_residential_with_scores(self):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building("residential")
        add_compliant_control_items(building_id, chapters=("Q1", "Q3", "Q4"))
        # Q3 系统评分满分 -> S3 = 100
        resp = client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q3-1", "chapter": "Q3",
            "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        assert resp.status_code == 200
        return category_ids, building_id

    def test_q3_facility_score_affects_q3(self, setup_db):
        """Q3 设施分应按 Q = S × (F/10) 计入 Q3，而非被忽略或计入 Q1"""
        category_ids, building_id = self._build_residential_with_scores()

        # 添加 Q3 居室设施，只得一半分 -> F3 = 5
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["居室"], "facility_name": "居室1"
        })
        facility_id = facility_resp.json()["id"]
        client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "7.3.1.2", "max_score": "10", "applicable_score": "10", "actual_score": "5"
        })

        result = client.post(f"/scoring/evaluate/{building_id}").json()
        assert result["eligible"] is True
        # Q3 = S3 × (F3/10) = 100 × 0.5 = 50
        assert Decimal(result["q3_score"]) == Decimal("50")

    def test_missing_chapter_facilities_neutral(self, setup_db):
        """参评章节无设施时 F 取中性值 10，Q = S（不折减也不归零）"""
        category_ids, building_id = self._build_residential_with_scores()

        # 只添加 Q1 设施，Q3 无设施 -> F3 = 10 中性
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        })
        facility_id = facility_resp.json()["id"]
        client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })

        result = client.post(f"/scoring/evaluate/{building_id}").json()
        assert result["eligible"] is True
        # Q3 = S3 × 10/10 = 100
        assert Decimal(result["q3_score"]) == Decimal("100")

    def test_q1_facility_score_not_polluted_by_other_chapters(self, setup_db):
        """Q3 设施分不应计入 Q1"""
        category_ids, building_id = self._build_residential_with_scores()

        # Q1 系统评分满分 + Q1 设施满分
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        })
        facility_id = facility_resp.json()["id"]
        client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        # Q3 居室设施 0 分 —— 若错误计入 Q1，会拉低 Q1
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["居室"], "facility_name": "居室1"
        })
        facility_id = facility_resp.json()["id"]
        client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "7.3.1.2", "max_score": "10", "applicable_score": "10", "actual_score": "0"
        })

        result = client.post(f"/scoring/evaluate/{building_id}").json()
        assert result["eligible"] is True
        # Q1 = 100 × (10/10) = 100，不受 Q3 设施 0 分影响
        assert Decimal(result["q1_score"]) == Decimal("100")
        # Q3 = 100 × (0/10) = 0
        assert Decimal(result["q3_score"]) == Decimal("0")


class TestScoreValidation:
    """分数范围校验"""

    def test_actual_score_exceeds_max_rejected(self, setup_db):
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "8", "applicable_score": "8", "actual_score": "10"
        })
        assert resp.status_code == 422

    def test_negative_score_rejected(self, setup_db):
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "8", "applicable_score": "8", "actual_score": "-1"
        })
        assert resp.status_code == 422

    def test_update_score_exceeds_max_rejected(self, setup_db):
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "8", "applicable_score": "8", "actual_score": "5"
        })
        item_id = resp.json()["id"]
        resp = client.put(f"/scoring/system-scores/{item_id}", json={"actual_score": "9"})
        assert resp.status_code == 400


class TestTemplateGeneration:
    """自动生成模板：建筑类型过滤 + 幂等"""

    def test_control_items_filtered_by_building_type(self, setup_db):
        """住宅建筑不应生成 Q2 控制项；条文适用类型应被遵守"""
        seed_standard_clause("5.1.1.1", "control", "control",
                             ["residential", "non_residential", "public_with_accom", "public_no_accom"], parent="Q1")
        seed_standard_clause("6.1.1.1", "control", "control",
                             ["non_residential", "public_with_accom", "public_no_accom"], parent="Q2")
        seed_standard_clause("7.1.1.1", "control", "control",
                             ["residential", "non_residential", "public_with_accom"], parent="Q3")

        _, building_id = create_project_and_building("residential")
        resp = client.post(f"/templates/generate-control-items/{building_id}")
        assert resp.status_code == 200
        items = resp.json()["items"]
        chapters = {i["chapter"] for i in items}
        assert "Q2" not in chapters
        assert chapters == {"Q1", "Q3"}

    def test_system_scores_respect_applicable_building_types(self, setup_db):
        """仅限公共建筑的条文（如5.2.1.3）不应为住宅生成"""
        seed_standard_clause("5.2.1.1", "Q1", "system",
                             ["residential", "non_residential", "public_with_accom", "public_no_accom"], max_score=8)
        seed_standard_clause("5.2.1.3", "Q1", "system",
                             ["public_with_accom", "public_no_accom"], max_score=6)

        _, building_id = create_project_and_building("residential")
        resp = client.post(f"/templates/generate-system-scores/{building_id}")
        assert resp.status_code == 200
        clause_ids = [i["clause_id"] for i in resp.json()["items"]]
        assert "5.2.1.1" in clause_ids
        assert "5.2.1.3" not in clause_ids

    def test_system_scores_include_q5_bonus_clauses(self, setup_db):
        """Q5创新与提升条文（bonus类型）应能被生成"""
        seed_standard_clause("11.1.1.5", "Q5", "bonus",
                             ["residential", "non_residential", "public_with_accom", "public_no_accom"], max_score=1)
        _, building_id = create_project_and_building("residential")
        resp = client.post(f"/templates/generate-system-scores/{building_id}")
        assert resp.status_code == 200
        clause_ids = [i["clause_id"] for i in resp.json()["items"]]
        assert "11.1.1.5" in clause_ids

    def test_generation_idempotent(self, setup_db):
        """重复生成不应产生重复记录"""
        seed_standard_clause("5.1.1.1", "control", "control",
                             ["residential"], parent="Q1")
        _, building_id = create_project_and_building("residential")
        resp1 = client.post(f"/templates/generate-control-items/{building_id}")
        resp2 = client.post(f"/templates/generate-control-items/{building_id}")
        assert len(resp1.json()["items"]) == 1
        assert len(resp2.json()["items"]) == 0

    def test_facility_score_generation(self, setup_db):
        """设施评分自动生成：存条文编号、可重复调用不重复"""
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        })
        facility_id = facility_resp.json()["id"]

        resp = client.post(f"/templates/generate-facility-scores/{facility_id}")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) > 0
        assert all(i["clause_id"] for i in items)

        # 再次生成不应重复
        resp2 = client.post(f"/templates/generate-facility-scores/{facility_id}")
        assert len(resp2.json()["items"]) == 0


class TestCompletionTimeRules:
    """完工时间（表2/表3）对检查项生成的影响"""

    def _create_building_with_clauses(self, within_one_year):
        from tests.conftest import TestingSessionLocal
        from app.models.models import Building
        # 9/10章控制项
        for num, parent in [("9.1.1.1", "construction"), ("10.1.1.1", "maintenance")]:
            seed_standard_clause(num, "control", "control",
                                 ["residential", "non_residential", "public_with_accom", "public_no_accom"],
                                 parent=parent)
        seed_standard_clause("5.1.1.1", "control", "control", ["residential"], parent="Q1")
        seed_standard_clause("9.2.1.1", "construction", "system",
                             ["residential"], max_score=20)
        seed_standard_clause("10.2.1.1", "maintenance", "system",
                             ["residential"], max_score=15)

        project_id = client.post("/projects/", json={
            "project_name": "测试项目", "evaluation_type": "initial"
        }).json()["id"]
        building_id = client.post("/buildings/", json={
            "project_id": project_id, "building_name": "测试楼",
            "building_type": "residential", "is_within_one_year": within_one_year,
            "site_inspection_passed": True if not within_one_year else None
        }).json()["id"]
        return building_id

    def test_within_one_year_includes_construction(self, setup_db):
        """竣工一年内：含施工验收控制项和评分项（表2）"""
        building_id = self._create_building_with_clauses(True)
        ci = client.post(f"/templates/generate-control-items/{building_id}").json()["items"]
        chapters = {i["chapter"] for i in ci}
        assert "construction" in chapters
        assert "maintenance" in chapters

        ss = client.post(f"/templates/generate-system-scores/{building_id}").json()["items"]
        ss_chapters = {i["chapter"] for i in ss}
        assert "construction" in ss_chapters
        assert "maintenance" in ss_chapters

    def test_after_one_year_excludes_construction(self, setup_db):
        """竣工一年后：不含施工验收，保留运行维护（表3）"""
        building_id = self._create_building_with_clauses(False)
        ci = client.post(f"/templates/generate-control-items/{building_id}").json()["items"]
        chapters = {i["chapter"] for i in ci}
        assert "construction" not in chapters
        assert "maintenance" in chapters

        ss = client.post(f"/templates/generate-system-scores/{building_id}").json()["items"]
        ss_chapters = {i["chapter"] for i in ss}
        assert "construction" not in ss_chapters
        assert "maintenance" in ss_chapters


class TestClauseLevelApplicability:
    """条文级建筑类型限制（如5.2.1.3仅公共建筑）在评价中生效"""

    def _setup_residential(self):
        category_ids = seed_facility_categories()
        # 适用所有类型的条文 + 仅公共建筑的条文
        c_all = seed_standard_clause("5.2.1.1", "Q1", "system",
                                     ["residential", "non_residential", "public_with_accom", "public_no_accom"], max_score=8)
        c_pub = seed_standard_clause("5.2.1.3", "Q1", "system",
                                     ["public_with_accom", "public_no_accom"], max_score=6)
        c_ctrl_all = seed_standard_clause("5.1.1.1", "control", "control", ["residential"], parent="Q1")
        c_ctrl_pub = seed_standard_clause("6.1.1.1", "control", "control",
                                          ["public_with_accom", "public_no_accom"], parent="Q2")

        _, building_id = create_project_and_building("residential")
        # 控制项：适用条文已达标；公共建筑专属条文未核查（旧数据遗留）
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": c_ctrl_all, "chapter": "Q1", "is_compliant": True})
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": c_ctrl_pub, "chapter": "Q2", "is_compliant": None})
        # 系统评分：5.2.1.1 得半分4/8；5.2.1.3 满分6/6（若被错误计入会拉高S1）
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": c_all, "chapter": "Q1", "max_score": "8", "applicable_score": "8", "actual_score": "4"})
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": c_pub, "chapter": "Q1", "max_score": "6", "applicable_score": "6", "actual_score": "6"})
        # Q1 设施满分
        fid = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"}).json()["id"]
        client.post(f"/scoring/facilities/{fid}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"})
        return building_id

    def test_evaluation_excludes_non_applicable_clauses(self, setup_db):
        """住宅评价：公共建筑专属条文不计入S1，未核查的公共控制项不卡闸门"""
        building_id = self._setup_residential()
        result = client.post(f"/scoring/evaluate/{building_id}").json()
        assert result["eligible"] is True  # 公共控制项未核查但被正确忽略
        # S1 = 4/8 × 100 = 50（不含5.2.1.3的6分），F1=10 → Q1 = 50
        assert Decimal(result["q1_score"]) == Decimal("50")

    def test_list_responses_include_applicable_types(self, setup_db):
        """列表接口返回条文适用建筑类型（供前端过滤）"""
        building_id = self._setup_residential()
        scores = client.get(f"/scoring/system-scores/{building_id}").json()
        pub_item = next(s for s in scores if s["clause_number"] == "5.2.1.3")
        assert pub_item["applicable_building_types"] == ["public_with_accom", "public_no_accom"]
        items = client.get(f"/scoring/control-items/{building_id}").json()
        ctrl = next(i for i in items if i["clause_number"] == "6.1.1.1")
        assert "residential" not in ctrl["applicable_building_types"]
