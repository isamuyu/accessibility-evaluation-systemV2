import pytest
from decimal import Decimal
from tests.conftest import (
    client, setup_db, seed_facility_categories, create_project_and_building,
    seed_standard_clause
)


class TestDeleteEndpoints:
    """DELETE 接口"""

    def test_delete_control_item(self, setup_db):
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "ctrl-1", "chapter": "Q1", "is_compliant": True
        })
        item_id = resp.json()["id"]
        assert client.delete(f"/scoring/control-items/{item_id}").status_code == 200
        assert client.get(f"/scoring/control-items/{building_id}").json() == []
        assert client.delete(f"/scoring/control-items/{item_id}").status_code == 404

    def test_delete_system_score(self, setup_db):
        _, building_id = create_project_and_building()
        resp = client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "8", "applicable_score": "8", "actual_score": "5"
        })
        item_id = resp.json()["id"]
        assert client.delete(f"/scoring/system-scores/{item_id}").status_code == 200
        assert client.get(f"/scoring/system-scores/{building_id}").json() == []

    def test_delete_facility_cascades_scores(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        score_id = client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "8"
        }).json()["id"]

        assert client.delete(f"/scoring/facilities/{facility_id}").status_code == 200
        assert client.get(f"/scoring/facilities/{building_id}").json() == []
        # 设施评分已级联删除
        assert client.delete(f"/scoring/facilities/scores/{score_id}").status_code == 404

    def test_delete_building_cascades(self, setup_db):
        category_ids = seed_facility_categories()
        project_id, building_id = create_project_and_building()
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "ctrl-1", "chapter": "Q1", "is_compliant": True
        })
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "8", "applicable_score": "8", "actual_score": "5"
        })

        assert client.delete(f"/buildings/{building_id}").status_code == 200
        assert client.get(f"/buildings/{building_id}").status_code == 404
        assert client.get(f"/scoring/control-items/{building_id}").json() == []

    def test_delete_project_with_buildings_rejected(self, setup_db):
        project_id, _ = create_project_and_building()
        resp = client.delete(f"/projects/{project_id}")
        assert resp.status_code == 400

    def test_delete_project(self, setup_db):
        project_id = client.post("/projects/", json={
            "project_name": "空项目", "evaluation_type": "initial"
        }).json()["id"]
        assert client.delete(f"/projects/{project_id}").status_code == 200
        assert client.get(f"/projects/{project_id}").status_code == 404

    def test_delete_clause_soft(self, setup_db):
        clause_id = seed_standard_clause("5.1.1.1", "control", "control", ["residential"], parent="Q1")
        assert client.delete(f"/standard-clauses/{clause_id}").status_code == 200
        # 软删除后按章节查询（只查 is_active）不再返回
        assert client.get("/standard-clauses/chapter/Q1").json() == []
        # 但记录本身仍可查询（保留历史引用）
        assert client.get(f"/standard-clauses/{clause_id}").status_code == 200


class TestFacilityScoreUpdate:
    """设施评分更新接口"""

    def test_update_facility_score(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        score_id = client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "0"
        }).json()["id"]

        resp = client.put(f"/scoring/facilities/scores/{score_id}", json={"actual_score": "8"})
        assert resp.status_code == 200
        assert Decimal(resp.json()["actual_score"]) == Decimal("8")

    def test_update_facility_score_exceeds_max_rejected(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        score_id = client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "0"
        }).json()["id"]
        assert client.put(f"/scoring/facilities/scores/{score_id}", json={"actual_score": "11"}).status_code == 400
        assert client.put(f"/scoring/facilities/scores/{score_id}", json={"actual_score": "-1"}).status_code in (400, 422)

    def test_update_facility_score_not_found(self, setup_db):
        assert client.put("/scoring/facilities/scores/nonexistent", json={"actual_score": "5"}).status_code == 404


class TestEvaluateIdempotency:
    """evaluate 幂等：输入不变时不重复生成结果行"""

    def _setup_evaluable_building(self):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "ctrl-1", "chapter": "Q1", "is_compliant": True
        })
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1-1", "chapter": "Q1",
            "max_score": "10", "applicable_score": "10", "actual_score": "8"
        })
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        return building_id

    def test_repeated_evaluate_no_duplicate_rows(self, setup_db):
        building_id = self._setup_evaluable_building()
        r1 = client.post(f"/scoring/evaluate/{building_id}").json()
        r2 = client.post(f"/scoring/evaluate/{building_id}").json()
        assert r1["eligible"] and r2["eligible"]
        assert r1["total_score_q"] == r2["total_score_q"]
        results = client.get(f"/scoring/results/{building_id}").json()
        assert len(results) == 1

    def test_evaluate_after_data_change_creates_new_row(self, setup_db):
        building_id = self._setup_evaluable_building()
        client.post(f"/scoring/evaluate/{building_id}")
        # 修改评分数据
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q4-1", "chapter": "Q4",
            "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        client.post(f"/scoring/evaluate/{building_id}")
        results = client.get(f"/scoring/results/{building_id}").json()
        assert len(results) == 2


class TestFacilityScoreDescription:
    """设施评分项应带条文描述"""

    def test_facility_scores_include_description(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        client.post(f"/templates/generate-facility-scores/{facility_id}")

        items = client.get(f"/scoring/facilities/{facility_id}/scores").json()
        assert len(items) > 0
        assert all(i["description"] for i in items)
        assert any("净宽" in i["description"] for i in items if i["clause_id"] == "5.3.1.3")


class TestScoreOptions:
    """单选评分档选项"""

    def test_system_scores_include_options(self, setup_db):
        clause_id = seed_standard_clause("5.2.1.1", "Q1", "system",
                                         ["residential"], max_score=8)
        # 手动给条文加 options
        from tests.conftest import TestingSessionLocal
        from app.models.models import StandardClause
        db = TestingSessionLocal()
        clause = db.query(StandardClause).filter(StandardClause.id == clause_id).first()
        clause.options = [{"label": "平坡", "score": 8}, {"label": "台阶+坡道", "score": 6}]
        db.commit()
        db.close()

        _, building_id = create_project_and_building("residential")
        client.post(f"/templates/generate-system-scores/{building_id}")
        scores = client.get(f"/scoring/system-scores/{building_id}").json()
        assert len(scores) == 1
        assert scores[0]["options"][0]["score"] == 8

    def test_facility_scores_include_options(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        # 出入口类别的 5.3.3.1 有选项
        from tests.conftest import TestingSessionLocal
        from app.models.models import FacilityCategory
        from app.core.enums import Chapter
        from decimal import Decimal
        db = TestingSessionLocal()
        cat = FacilityCategory(category_code="出入口", category_name="无障碍出入口", chapter=Chapter.Q1, max_score=Decimal("10"))
        db.add(cat)
        db.commit()
        cat_id = cat.id
        db.close()

        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": cat_id, "facility_name": "出入口1"
        }).json()["id"]
        client.post(f"/templates/generate-facility-scores/{facility_id}")
        items = client.get(f"/scoring/facilities/{facility_id}/scores").json()
        opt_item = next(i for i in items if i["clause_id"] == "5.3.3.1")
        assert opt_item["options"] is not None
        assert opt_item["options"][0]["score"] == 3


class TestIsScored:
    """is_scored 标记：区分未评分与评了0分"""

    def test_generated_items_not_scored(self, setup_db):
        seed_standard_clause("5.2.1.1", "Q1", "system", ["residential"], max_score=8)
        _, building_id = create_project_and_building("residential")
        client.post(f"/templates/generate-system-scores/{building_id}")
        scores = client.get(f"/scoring/system-scores/{building_id}").json()
        assert scores[0]["is_scored"] is False

    def test_scoring_zero_marks_scored(self, setup_db):
        seed_standard_clause("5.2.1.1", "Q1", "system", ["residential"], max_score=8)
        _, building_id = create_project_and_building("residential")
        client.post(f"/templates/generate-system-scores/{building_id}")
        scores = client.get(f"/scoring/system-scores/{building_id}").json()
        item_id = scores[0]["id"]

        # 评0分（不符合）→ is_scored=True
        resp = client.put(f"/scoring/system-scores/{item_id}", json={"actual_score": "0"})
        assert resp.status_code == 200
        assert resp.json()["is_scored"] is True
        assert Decimal(resp.json()["actual_score"]) == Decimal("0")

    def test_facility_score_zero_marks_scored(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building()
        facility_id = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"
        }).json()["id"]
        score_id = client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "0"
        }).json()["id"]
        resp = client.put(f"/scoring/facilities/scores/{score_id}", json={"actual_score": "0"})
        assert resp.json()["is_scored"] is True


class TestBuildingAttrChangeReevaluate:
    """建筑属性变化（现场检测/完工时间）后重新评价应生成新结果"""

    def test_site_inspection_change_creates_new_result(self, setup_db):
        category_ids = seed_facility_categories()
        project_id = client.post("/projects/", json={
            "project_name": "测试项目", "evaluation_type": "initial"}).json()["id"]
        building_id = client.post("/buildings/", json={
            "project_id": project_id, "building_name": "测试楼",
            "building_type": "public_no_accom", "is_within_one_year": False,
            "site_inspection_passed": None}).json()["id"]

        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "c1", "chapter": "Q1", "is_compliant": True})
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q1", "chapter": "Q1",
            "max_score": "10", "applicable_score": "10", "actual_score": "8"})
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q2", "chapter": "Q2",
            "max_score": "10", "applicable_score": "10", "actual_score": "8"})
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "q4", "chapter": "Q4",
            "max_score": "10", "applicable_score": "10", "actual_score": "8"})
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "m1", "chapter": "maintenance",
            "max_score": "10", "applicable_score": "10", "actual_score": "8"})
        fid = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"}).json()["id"]
        client.post(f"/scoring/facilities/{fid}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"})

        # 第一次：未登记现场检测 → none
        r1 = client.post(f"/scoring/evaluate/{building_id}").json()
        assert r1["grade"] == "none"

        # 登记现场检测合格 → 重新评价应生成新结果且等级更新
        client.put(f"/buildings/{building_id}", json={"site_inspection_passed": True})
        r2 = client.post(f"/scoring/evaluate/{building_id}").json()
        assert r2["grade"] != "none"

        results = client.get(f"/scoring/results/{building_id}").json()
        assert len(results) == 2
        assert results[0]["determined_grade"] != "none"  # 最新结果在前


class TestFailedEvaluationRecorded:
    """控制项未通过时应写入不达标结果（覆盖旧等级）"""

    def test_gate_failure_overwrites_old_grade(self, setup_db):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building("public_no_accom")
        ctrl = client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "c1", "chapter": "Q1", "is_compliant": True}).json()
        for ch in ["Q1", "Q2", "Q4", "construction", "maintenance"]:
            client.post(f"/scoring/system-scores/{building_id}", json={
                "clause_id": ch, "chapter": ch,
                "max_score": "10", "applicable_score": "10", "actual_score": "8"})
        fid = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"}).json()["id"]
        client.post(f"/scoring/facilities/{fid}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"})

        # 先评出等级
        r1 = client.post(f"/scoring/evaluate/{building_id}").json()
        assert r1["grade"] != "none"

        # 控制项改为不达标 → 评价未通过，但结果应更新为 none
        client.put(f"/scoring/control-items/{ctrl['id']}", json={"is_compliant": False})
        r2 = client.post(f"/scoring/evaluate/{building_id}").json()
        assert r2["eligible"] is False
        latest = client.get(f"/scoring/results/{building_id}").json()[0]
        assert latest["determined_grade"] == "none"
        assert "未达标" in latest["breakdown"]["reason"]

        # 再次评价（同样未通过）→ 幂等，不重复写行
        count_before = len(client.get(f"/scoring/results/{building_id}").json())
        client.post(f"/scoring/evaluate/{building_id}")
        count_after = len(client.get(f"/scoring/results/{building_id}").json())
        assert count_before == count_after


class TestComplexBuildingFull:
    """建筑群综合评价（4.2.1.10）"""

    def _make_evaluated_building(self, project_id, name, area, q_score, within=True):
        category_ids = seed_facility_categories()
        building_id = client.post("/buildings/", json={
            "project_id": project_id, "building_name": name,
            "building_type": "public_no_accom", "floor_area": str(area),
            "is_within_one_year": within, "site_inspection_passed": None if within else True}).json()["id"]
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "c1", "chapter": "Q1", "is_compliant": True})
        # 用统一分值控制Q：actual=max*q_score/100
        for ch in ["Q1", "Q2", "Q4", "construction", "maintenance"]:
            client.post(f"/scoring/system-scores/{building_id}", json={
                "clause_id": f"{name}-{ch}", "chapter": ch,
                "max_score": "100", "applicable_score": "100", "actual_score": str(q_score)})
        fid = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道"}).json()["id"]
        client.post(f"/scoring/facilities/{fid}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"})
        client.post(f"/scoring/evaluate/{building_id}")
        return building_id

    def test_complex_full_evaluation(self, setup_db):
        """Z1/Z2/ZQ + 加权维度 + 等级认定"""
        project_id = client.post("/projects/", json={
            "project_name": "建筑群测试", "evaluation_type": "initial"}).json()["id"]
        # 两栋：Q=70(2000㎡)、Q=90(3000㎡) → Z1=82；Z2=75 → ZQ=82*0.8+75*0.2=80.6
        self._make_evaluated_building(project_id, "A栋", 2000, 70)
        self._make_evaluated_building(project_id, "B栋", 3000, 90)

        resp = client.post(f"/scoring/complex/{project_id}?z2_score=75")
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["z1_score"]) == Decimal("82.00")
        assert Decimal(data["z2_score"]) == Decimal("75.00")
        assert Decimal(data["zq_score"]) == Decimal("80.60")
        assert data["determined_grade"] is not None
        assert data["dimension_scores"]["q1"] is not None
        assert len(data["building_scores"]) == 2

        # 可查询最新结果
        get_resp = client.get(f"/scoring/complex/{project_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["zq_score"] == data["zq_score"]

    def test_complex_precondition_q40(self, setup_db):
        """单体Q<40时不满足建筑群评价前提"""
        project_id = client.post("/projects/", json={
            "project_name": "建筑群测试2", "evaluation_type": "initial"}).json()["id"]
        self._make_evaluated_building(project_id, "低分栋", 2000, 30)
        resp = client.post(f"/scoring/complex/{project_id}")
        assert resp.status_code == 400
        assert "Q < 40" in resp.json()["detail"]

    def test_complex_unevaluated_building_rejected(self, setup_db):
        project_id = client.post("/projects/", json={
            "project_name": "建筑群测试3", "evaluation_type": "initial"}).json()["id"]
        client.post("/buildings/", json={
            "project_id": project_id, "building_name": "未评楼",
            "building_type": "residential", "floor_area": "1000"})
        resp = client.post(f"/scoring/complex/{project_id}")
        assert resp.status_code == 400
        assert "尚未评价" in resp.json()["detail"]
