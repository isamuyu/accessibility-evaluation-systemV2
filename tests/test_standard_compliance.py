import pytest
from decimal import Decimal
from app.data.standard_data import STANDARD_CLAUSES, FACILITY_CLAUSES
from app.services.scoring_engine import ScoringEngine
from app.core.enums import Grade


class TestStandardDataIntegrity:
    """种子数据与 T/CNAEC 1304—2022 原文一致性"""

    def _chapter_total(self, chapter):
        return sum(
            Decimal(str(c["max_score"])) for c in STANDARD_CLAUSES
            if c["chapter"] == chapter
        )

    def test_q1_system_total_100(self):
        assert self._chapter_total("Q1") == Decimal("100")

    def test_q2_system_total_100(self):
        assert self._chapter_total("Q2") == Decimal("100")

    def test_q3_system_total_100(self):
        assert self._chapter_total("Q3") == Decimal("100")

    def test_q4_system_total_100(self):
        assert self._chapter_total("Q4") == Decimal("100")

    def test_construction_total_100(self):
        assert self._chapter_total("construction") == Decimal("100")

    def test_maintenance_total_100(self):
        assert self._chapter_total("maintenance") == Decimal("100")

    def test_q5_total_at_least_20(self):
        """Q5 上限20分，条文总分应不少于20（11章总分20.5，由引擎截断到20）"""
        total = self._chapter_total("Q5")
        assert total >= Decimal("20")

    def test_clause_numbers_unique(self):
        numbers = [c["clause_number"] for c in STANDARD_CLAUSES]
        assert len(numbers) == len(set(numbers))

    def test_maintenance_clause_scores_match_standard(self):
        """10.2.x 分值与原文一致"""
        expected = {
            "10.2.1.1": 15, "10.2.1.2": 15, "10.2.2.1": 30,
            "10.2.2.2": 10, "10.2.3.1": 20, "10.2.3.2": 10,
        }
        for number, score in expected.items():
            clause = next(c for c in STANDARD_CLAUSES if c["clause_number"] == number)
            assert Decimal(str(clause["max_score"])) == Decimal(score), number

    def test_facility_categories_total_10(self):
        """每类设施评分项满分应为10分（原文各节均为10分）"""
        for category, clauses in FACILITY_CLAUSES.items():
            total = sum(Decimal(str(c["max_score"])) for c in clauses)
            assert total == Decimal("10"), f"{category}: {total}"

    def test_facility_clause_numbers_unique_within_category(self):
        for category, clauses in FACILITY_CLAUSES.items():
            numbers = [c["clause_number"] for c in clauses]
            assert len(numbers) == len(set(numbers)), category

    def test_q2_clauses_not_for_residential(self):
        """Q2 条文不应适用于住宅类"""
        for c in STANDARD_CLAUSES:
            if c["chapter"] == "Q2":
                assert "residential" not in c["applicable"], c["clause_number"]

    def test_q3_clauses_not_for_public_no_accom(self):
        """Q3 条文不应适用于不含住宿功能的公共建筑"""
        for c in STANDARD_CLAUSES:
            if c["chapter"] == "Q3":
                assert "public_no_accom" not in c["applicable"], c["clause_number"]


class TestGradeTable3:
    """表3（竣工一年后）等级认定"""

    def _grade(self, **kwargs):
        defaults = dict(
            Q=Decimal("85"), q1=Decimal("65"), q2=Decimal("70"),
            q3=Decimal("65"), q4=Decimal("65"),
            construction_score=Decimal("50"), maintenance_score=Decimal("85"),
            within_one_year=False, site_inspection_passed=True,
        )
        defaults.update(kwargs)
        return ScoringEngine.determine_grade(**defaults)

    def test_after_one_year_construction_not_required(self):
        """一年后评价不要求施工验收分（表3无此项）"""
        grade, _ = self._grade(construction_score=Decimal("0"))
        assert grade == Grade.THREE_STAR

    def test_after_one_year_maintenance_still_required(self):
        """一年后评价仍要求运行维护分"""
        grade, _ = self._grade(maintenance_score=Decimal("75"))
        assert grade == Grade.TWO_STAR
        grade, _ = self._grade(maintenance_score=Decimal("65"))
        assert grade == Grade.ONE_STAR
        grade, _ = self._grade(maintenance_score=Decimal("50"))
        assert grade == Grade.NONE

    def test_after_one_year_site_inspection_required(self):
        """一年后评价须现场检测合格"""
        grade, _ = self._grade(site_inspection_passed=False)
        assert grade == Grade.NONE
        grade, _ = self._grade(site_inspection_passed=None)
        assert grade == Grade.NONE

    def test_multi_level_downgrade(self):
        """多级降级：三星水平 + 施工65分 → 应降为一星（原逻辑只降到二星）"""
        grade, _ = self._grade(
            within_one_year=True, site_inspection_passed=None,
            construction_score=Decimal("65"), maintenance_score=Decimal("85"),
        )
        assert grade == Grade.ONE_STAR

    def test_downgrade_to_none(self):
        """施工/运维任一低于60 → 不予评级"""
        grade, _ = self._grade(
            within_one_year=True, site_inspection_passed=None,
            construction_score=Decimal("50"), maintenance_score=Decimal("85"),
        )
        assert grade == Grade.NONE

    def test_maintenance_limits_within_one_year(self):
        """一年内运维分同样限制等级"""
        grade, _ = self._grade(
            within_one_year=True, site_inspection_passed=None,
            construction_score=Decimal("85"), maintenance_score=Decimal("65"),
        )
        assert grade == Grade.ONE_STAR


class TestComplexScoreZ2:
    """建筑群 Z2 参数"""

    def test_z2_parameter(self):
        buildings = [
            {"id": "b1", "name": "A栋", "Q": Decimal("70"), "floor_area": Decimal("2000")},
            {"id": "b2", "name": "B栋", "Q": Decimal("80"), "floor_area": Decimal("3000")},
        ]
        # Z1 = 70*0.4 + 80*0.6 = 76; ZQ = 76*0.8 + 75*0.2 = 75.8
        Z1, Z2, ZQ, _ = ScoringEngine.calc_complex_building_score(buildings, z2=Decimal("75"))
        assert Z1 == Decimal("76.00")
        assert Z2 == Decimal("75.00")
        assert ZQ == Decimal("75.80")

    def test_z2_default(self):
        buildings = [
            {"id": "b1", "name": "A栋", "Q": Decimal("70"), "floor_area": Decimal("2000")},
        ]
        _, Z2, _, _ = ScoringEngine.calc_complex_building_score(buildings)
        assert Z2 == Decimal("80.00")
