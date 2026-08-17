import io
import pytest
from tests.conftest import (
    client, setup_db, seed_facility_categories, create_project_and_building
)


def _evaluated_building():
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
    client.post(f"/scoring/evaluate/{building_id}")
    return building_id


class TestReports:
    def test_building_report(self, setup_db):
        building_id = _evaluated_building()
        resp = client.get(f"/reports/building/{building_id}")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "测试楼" in resp.text
        assert "评价等级" in resp.text

    def test_report_without_evaluation_404(self, setup_db):
        _, building_id = create_project_and_building()
        assert client.get(f"/reports/building/{building_id}").status_code == 404

    def test_report_building_not_found(self, setup_db):
        assert client.get("/reports/building/nonexistent").status_code == 404


class TestUploads:
    def test_upload_image(self, setup_db):
        content = b"\x89PNG\r\n\x1a\n" + b"0" * 100
        resp = client.post("/uploads/", files={"file": ("photo.png", io.BytesIO(content), "image/png")})
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"].endswith(".png")
        assert data["size"] == len(content)

    def test_upload_disallowed_type_rejected(self, setup_db):
        resp = client.post("/uploads/", files={"file": ("evil.exe", io.BytesIO(b"MZ"), "application/octet-stream")})
        assert resp.status_code == 400

    def test_upload_empty_file_rejected(self, setup_db):
        resp = client.post("/uploads/", files={"file": ("empty.png", io.BytesIO(b""), "image/png")})
        assert resp.status_code == 400


class TestSuggestionsAndPdf:
    """改善建议 + PDF报告"""

    def _building_with_lost_scores(self):
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building("non_residential")
        # 控制项达标
        client.post(f"/scoring/control-items/{building_id}", json={
            "clause_id": "ctrl-1", "chapter": "Q1", "is_compliant": True})
        # 系统评分：6.2.1.3（电动轮椅充电设施，4星0成本）得0分
        client.post(f"/scoring/system-scores/{building_id}", json={
            "clause_id": "x1", "chapter": "Q2",
            "max_score": "3", "applicable_score": "3", "actual_score": "0"})
        # 设施满分（满足评价前置）
        fid = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"], "facility_name": "通道1"}).json()["id"]
        client.post(f"/scoring/facilities/{fid}/scores", json={
            "clause_id": "5.3.6.2b", "max_score": "1", "applicable_score": "1", "actual_score": "0"})
        return building_id

    def test_suggestions_sorted_by_stars(self, setup_db):
        building_id = self._building_with_lost_scores()
        resp = client.get(f"/reports/building/{building_id}/suggestions")
        assert resp.status_code == 200
        suggestions = resp.json()["suggestions"]
        assert len(suggestions) >= 2
        stars = [s["stars"] for s in suggestions]
        assert stars == sorted(stars, reverse=True)
        # 5.3.6.2b 是4星（0成本-非机动车不占用盲道）
        fac_sg = next(s for s in suggestions if s["clause_number"] == "5.3.6.2b")
        assert fac_sg["stars"] == 4
        assert "非机动车" in fac_sg["content"]

    def test_pdf_report(self, setup_db):
        building_id = self._building_with_lost_scores()
        client.post(f"/scoring/evaluate/{building_id}")
        resp = client.get(f"/reports/building/{building_id}/pdf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content[:5] == b"%PDF-"

    def test_pdf_report_no_result_404(self, setup_db):
        _, building_id = create_project_and_building()
        assert client.get(f"/reports/building/{building_id}/pdf").status_code == 404
