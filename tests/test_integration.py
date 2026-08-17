import pytest
from tests.conftest import (
    client, setup_db, seed_facility_categories, create_project_and_building
)


class TestIntegration:
    """集成测试"""
    
    def test_health_check(self, setup_db):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_project(self, setup_db):
        """测试创建项目"""
        data = {
            "project_name": "测试项目",
            "project_code": "TEST001",
            "applicant_name": "张三",
            "applicant_contact": "13800138000",
            "evaluation_type": "initial"
        }
        response = client.post("/projects/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["project_name"] == "测试项目"
        assert result["status"] == "draft"
        assert result["id"]
    
    def test_create_building(self, setup_db):
        """测试创建建筑"""
        # 先创建项目
        project_data = {
            "project_name": "测试项目",
            "evaluation_type": "initial"
        }
        project_resp = client.post("/projects/", json=project_data)
        project_id = project_resp.json()["id"]
        
        # 创建建筑
        building_data = {
            "project_id": project_id,
            "building_name": "1号楼",
            "building_type": "residential",
            "floor_area": "10000.00",
            "is_within_one_year": True
        }
        response = client.post("/buildings/", json=building_data)
        assert response.status_code == 200
        result = response.json()
        assert result["building_name"] == "1号楼"
        assert result["building_type"] == "residential"
    
    def test_standard_clause_crud(self, setup_db):
        """测试标准条文CRUD"""
        # 创建条文
        clause_data = {
            "clause_number": "5.2.1.1",
            "chapter": "Q1",
            "clause_type": "system",
            "description": "测试条文",
            "max_score": "8",
            "score_type": "single_choice"
        }
        response = client.post("/standard-clauses/", json=clause_data)
        assert response.status_code == 200
        
        # 查询条文
        response = client.get("/standard-clauses/")
        assert response.status_code == 200
        assert len(response.json()) >= 1
        
        # 按章节查询
        response = client.get("/standard-clauses/chapter/Q1")
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_full_evaluation_flow(self, setup_db):
        """测试完整评价流程"""
        category_ids = seed_facility_categories()
        _, building_id = create_project_and_building("public_no_accom")

        # 3. 添加控制项（全部达标）
        control_items = [
            {"clause_id": "clause-1", "chapter": "Q1", "is_compliant": True},
            {"clause_id": "clause-2", "chapter": "Q1", "is_compliant": True},
            {"clause_id": "clause-3", "chapter": "Q2", "is_compliant": True},
        ]
        for item in control_items:
            response = client.post(f"/scoring/control-items/{building_id}", json=item)
            assert response.status_code == 200

        # 4. 添加系统评分
        scores = [
            {"clause_id": "q1-1", "chapter": "Q1", "max_score": "8", "applicable_score": "8", "actual_score": "8"},
            {"clause_id": "q1-2", "chapter": "Q1", "max_score": "8", "applicable_score": "8", "actual_score": "6"},
            {"clause_id": "q2-1", "chapter": "Q2", "max_score": "10", "applicable_score": "10", "actual_score": "8"},
            {"clause_id": "q4-1", "chapter": "Q4", "max_score": "10", "applicable_score": "10", "actual_score": "10"},
            {"clause_id": "c-1", "chapter": "construction", "max_score": "20", "applicable_score": "20", "actual_score": "18"},
            {"clause_id": "m-1", "chapter": "maintenance", "max_score": "20", "applicable_score": "20", "actual_score": "16"},
        ]
        for score in scores:
            response = client.post(f"/scoring/system-scores/{building_id}", json=score)
            assert response.status_code == 200

        # 5. 添加设施及设施评分（Q1 通道，满分）
        facility_resp = client.post(f"/scoring/facilities/{building_id}", json={
            "category_id": category_ids["通道"],
            "facility_name": "主通道",
            "location_description": "一层"
        })
        assert facility_resp.status_code == 200
        facility_id = facility_resp.json()["id"]
        response = client.post(f"/scoring/facilities/{facility_id}/scores", json={
            "clause_id": "5.3.1.3", "max_score": "10", "applicable_score": "10", "actual_score": "10"
        })
        assert response.status_code == 200

        # 6. 执行评价
        response = client.post(f"/scoring/evaluate/{building_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["eligible"] is True
        assert "grade" in result
        assert "total_score_q" in result

        # 7. 查询评价结果
        response = client.get(f"/scoring/results/{building_id}")
        assert response.status_code == 200
        assert len(response.json()) >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])