import pytest
from decimal import Decimal
from app.services.scoring_engine import (
    ScoringEngine, ScoreItem, Facility,
    StrategyFactory, ResidentialStrategy, PublicNoAccomStrategy
)
from app.core.enums import BuildingType, Grade

class TestScoringEngine:
    """评分引擎测试"""
    
    def test_check_control_items_pass(self):
        """测试控制项全部通过"""
        items = [
            {"clause_id": "5.1.1.1", "is_compliant": True},
            {"clause_id": "5.1.1.2", "is_compliant": True},
            {"clause_id": "5.1.1.3", "is_compliant": True},
        ]
        passed, reason = ScoringEngine.check_control_items(items)
        assert passed is True
        assert reason is None
    
    def test_check_control_items_fail(self):
        """测试控制项未通过"""
        items = [
            {"clause_id": "5.1.1.1", "is_compliant": True},
            {"clause_id": "5.1.1.2", "is_compliant": False},
        ]
        passed, reason = ScoringEngine.check_control_items(items)
        assert passed is False
        assert "5.1.1.2" in reason
    
    def test_calc_system_score_full(self):
        """测试系统评分满分"""
        items = [
            ScoreItem("5.2.1.1", "", Decimal("8"), Decimal("8"), True),
            ScoreItem("5.2.1.2", "", Decimal("8"), Decimal("8"), True),
        ]
        score = ScoringEngine.calc_system_score(items)
        assert score == Decimal("100.00")
    
    def test_calc_system_score_partial(self):
        """测试系统评分部分得分"""
        items = [
            ScoreItem("5.2.1.1", "", Decimal("8"), Decimal("4"), True),
            ScoreItem("5.2.1.2", "", Decimal("8"), Decimal("8"), True),
        ]
        score = ScoringEngine.calc_system_score(items)
        assert score == Decimal("75.00")
    
    def test_calc_system_score_with_not_applicable(self):
        """测试有不参评项的系统评分"""
        items = [
            ScoreItem("5.2.1.1", "", Decimal("8"), Decimal("8"), True),
            ScoreItem("5.2.1.3", "", Decimal("6"), Decimal("0"), False),  # 不适用
        ]
        score = ScoringEngine.calc_system_score(items)
        assert score == Decimal("100.00")
    
    def test_facility_normalized_score(self):
        """测试设施归一化评分"""
        items = [
            ScoreItem("5.3.1.1a", "", Decimal("1"), Decimal("1"), True),
            ScoreItem("5.3.1.1b", "", Decimal("1"), Decimal("0"), True),
            ScoreItem("5.3.1.1c", "", Decimal("1"), Decimal("1"), True),
        ]
        facility = Facility("f1", "通道", "1层", items)
        assert facility.applicable_max == Decimal("3")
        assert facility.actual == Decimal("2")
        assert facility.normalized_score == Decimal("6.67")
    
    def test_calc_facility_score(self):
        """测试设施分计算"""
        f1_items = [ScoreItem("5.3.1.1a", "", Decimal("1"), Decimal("1"), True)]
        f2_items = [ScoreItem("5.3.1.1b", "", Decimal("1"), Decimal("1"), True)]
        
        facilities = {
            "通道": [
                Facility("f1", "通道", "1层", f1_items),
                Facility("f2", "通道", "2层", f1_items),
            ],
            "坡道": [
                Facility("f3", "坡道", "入口", f2_items),
            ]
        }
        
        score = ScoringEngine.calc_facility_score(facilities)
        # 通道类平均: (10 + 10) / 2 = 10
        # 坡道类平均: 10
        # 总体平均: (10 + 10) / 2 = 10
        assert score == Decimal("10.00")
    
    def test_calc_Qx(self):
        """测试维度分Q计算"""
        S = Decimal("80")
        F = Decimal("8")
        Q = ScoringEngine.calc_Qx(S, F)
        assert Q == Decimal("64.00")
    
    def test_calc_Q5_with_cap(self):
        """测试Q5上限"""
        items = [
            ScoreItem("11.1.1.1", "", Decimal("1"), Decimal("1"), True),
            ScoreItem("11.1.1.2", "", Decimal("0.5"), Decimal("0.5"), True),
        ]
        score = ScoringEngine.calc_Q5(items)
        assert score == Decimal("1.50")
        
        # 测试超过上限
        items_large = [ScoreItem(f"11.1.1.{i}", "", Decimal("1"), Decimal("1"), True) for i in range(25)]
        score_large = ScoringEngine.calc_Q5(items_large)
        assert score_large == Decimal("20.00")
    
    def test_residential_strategy(self):
        """测试住宅策略"""
        strategy = ResidentialStrategy()
        chapters = strategy.get_applicable_chapters()
        assert len(chapters) == 4
        
        scores = {"Q1": Decimal("60"), "Q3": Decimal("70"), "Q4": Decimal("80"), "Q5": Decimal("10")}
        total = strategy.get_total_formula(scores)
        assert total == Decimal("80.00")
    
    def test_public_no_accom_strategy(self):
        """测试不含住宿公共建筑策略"""
        strategy = PublicNoAccomStrategy()
        chapters = strategy.get_applicable_chapters()
        assert len(chapters) == 4
        
        scores = {"Q1": Decimal("60"), "Q2": Decimal("70"), "Q4": Decimal("80"), "Q5": Decimal("10")}
        total = strategy.get_total_formula(scores)
        assert total == Decimal("80.00")
    
    def test_strategy_factory(self):
        """测试策略工厂"""
        strategy = StrategyFactory.get_strategy(BuildingType.RESIDENTIAL)
        assert isinstance(strategy, ResidentialStrategy)
        
        strategy = StrategyFactory.get_strategy(BuildingType.PUBLIC_NO_ACCOM)
        assert isinstance(strategy, PublicNoAccomStrategy)
    
    def test_determine_grade_one_star(self):
        """测试一星级认定"""
        grade, _ = ScoringEngine.determine_grade(
            Q=Decimal("45"),
            q1=Decimal("25"),
            q2=None,
            q3=Decimal("30"),
            q4=Decimal("25"),
            construction_score=Decimal("65"),
            maintenance_score=Decimal("65"),
            within_one_year=True
        )
        assert grade == Grade.ONE_STAR
    
    def test_determine_grade_two_star(self):
        """测试二星级认定"""
        grade, _ = ScoringEngine.determine_grade(
            Q=Decimal("65"),
            q1=Decimal("45"),
            q2=Decimal("50"),
            q3=None,
            q4=Decimal("45"),
            construction_score=Decimal("75"),
            maintenance_score=Decimal("75"),
            within_one_year=True
        )
        assert grade == Grade.TWO_STAR
    
    def test_determine_grade_three_star(self):
        """测试三星级认定"""
        grade, _ = ScoringEngine.determine_grade(
            Q=Decimal("85"),
            q1=Decimal("65"),
            q2=Decimal("70"),
            q3=Decimal("65"),
            q4=Decimal("65"),
            construction_score=Decimal("85"),
            maintenance_score=Decimal("85"),
            within_one_year=True
        )
        assert grade == Grade.THREE_STAR
    
    def test_determine_grade_none(self):
        """测试不达标"""
        grade, _ = ScoringEngine.determine_grade(
            Q=Decimal("35"),
            q1=Decimal("15"),
            q2=None,
            q3=Decimal("20"),
            q4=Decimal("15"),
            construction_score=Decimal("50"),
            maintenance_score=Decimal("50"),
            within_one_year=True
        )
        assert grade == Grade.NONE
    
    def test_calc_complex_building_score(self):
        """测试建筑群综合评分"""
        buildings = [
            {"id": "b1", "name": "A栋", "Q": Decimal("70"), "floor_area": Decimal("10000")},
            {"id": "b2", "name": "B栋", "Q": Decimal("80"), "floor_area": Decimal("20000")},
        ]
        
        Z1, Z2, ZQ, scores = ScoringEngine.calc_complex_building_score(buildings)
        
        # Z1 = (70*10000 + 80*20000) / 30000 = 76.67
        assert Z1 == Decimal("76.67")
        assert ZQ > Z1  # ZQ = Z1*0.8 + Z2*0.2
    
    def test_calc_complex_building_score_fail(self):
        """测试建筑群评分前提不满足"""
        buildings = [
            {"id": "b1", "name": "A栋", "Q": Decimal("35"), "floor_area": Decimal("10000")},
        ]
        
        with pytest.raises(ValueError) as exc_info:
            ScoringEngine.calc_complex_building_score(buildings)
        
        assert "Q < 40" in str(exc_info.value)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])