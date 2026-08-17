from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from app.core.enums import *

@dataclass
class ScoreItem:
    clause: str
    description: str
    max_score: Decimal
    actual_score: Decimal
    applicable: bool
    evidence: str = ""

@dataclass
class Facility:
    id: str
    category: str
    location: str
    score_items: List[ScoreItem]
    
    @property
    def applicable_max(self) -> Decimal:
        return sum(
            (item.max_score for item in self.score_items if item.applicable),
            Decimal("0")
        )
    
    @property
    def actual(self) -> Decimal:
        return sum(
            (item.actual_score for item in self.score_items if item.applicable),
            Decimal("0")
        )
    
    @property
    def normalized_score(self) -> Decimal:
        if self.applicable_max == 0:
            return Decimal("0")
        return (self.actual / self.applicable_max * 10).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class BuildingTypeStrategy:
    """建筑类型策略接口"""
    
    def get_applicable_chapters(self) -> List[Chapter]:
        raise NotImplementedError
    
    def get_total_formula(self, scores: Dict[str, Decimal]) -> Decimal:
        raise NotImplementedError
    
    def get_required_facility_categories(self) -> List[str]:
        raise NotImplementedError
    
    def get_divisor(self) -> int:
        raise NotImplementedError

class ResidentialStrategy(BuildingTypeStrategy):
    """住宅类居住建筑策略"""
    
    def get_applicable_chapters(self) -> List[Chapter]:
        return [Chapter.Q1, Chapter.Q3, Chapter.Q4, Chapter.Q5]
    
    def get_total_formula(self, scores: Dict[str, Decimal]) -> Decimal:
        base = (scores.get("Q1", Decimal("0")) + 
                scores.get("Q3", Decimal("0")) + 
                scores.get("Q4", Decimal("0"))) / Decimal("3")
        return base + scores.get("Q5", Decimal("0"))
    
    def get_required_facility_categories(self) -> List[str]:
        return ["通道", "坡道", "出入口", "门", "电梯", "盲道", "其他通行设施", "居室", "无障碍卫生间"]
    
    def get_divisor(self) -> int:
        return 3

class NonResidentialStrategy(BuildingTypeStrategy):
    """非住宅类居住建筑策略"""
    
    def get_applicable_chapters(self) -> List[Chapter]:
        return [Chapter.Q1, Chapter.Q2, Chapter.Q3, Chapter.Q4, Chapter.Q5]
    
    def get_total_formula(self, scores: Dict[str, Decimal]) -> Decimal:
        base = (scores.get("Q1", Decimal("0")) + 
                scores.get("Q2", Decimal("0")) + 
                scores.get("Q3", Decimal("0")) + 
                scores.get("Q4", Decimal("0"))) / Decimal("4")
        return base + scores.get("Q5", Decimal("0"))
    
    def get_required_facility_categories(self) -> List[str]:
        return ["通道", "坡道", "出入口", "门", "电梯", "盲道", "其他通行设施",
                "公共卫生间", "无障碍厕所", "公共浴室", "轮椅席位", "居室", "无障碍卫生间"]
    
    def get_divisor(self) -> int:
        return 4

class PublicWithAccomStrategy(BuildingTypeStrategy):
    """含住宿功能的公共建筑策略"""
    
    def get_applicable_chapters(self) -> List[Chapter]:
        return [Chapter.Q1, Chapter.Q2, Chapter.Q3, Chapter.Q4, Chapter.Q5]
    
    def get_total_formula(self, scores: Dict[str, Decimal]) -> Decimal:
        base = (scores.get("Q1", Decimal("0")) + 
                scores.get("Q2", Decimal("0")) + 
                scores.get("Q3", Decimal("0")) + 
                scores.get("Q4", Decimal("0"))) / Decimal("4")
        return base + scores.get("Q5", Decimal("0"))
    
    def get_required_facility_categories(self) -> List[str]:
        return ["通道", "坡道", "出入口", "门", "电梯", "盲道", "其他通行设施",
                "公共卫生间", "无障碍厕所", "公共浴室", "轮椅席位", "居室", "无障碍卫生间"]
    
    def get_divisor(self) -> int:
        return 4

class PublicNoAccomStrategy(BuildingTypeStrategy):
    """不含住宿功能的公共建筑策略"""
    
    def get_applicable_chapters(self) -> List[Chapter]:
        return [Chapter.Q1, Chapter.Q2, Chapter.Q4, Chapter.Q5]
    
    def get_total_formula(self, scores: Dict[str, Decimal]) -> Decimal:
        base = (scores.get("Q1", Decimal("0")) + 
                scores.get("Q2", Decimal("0")) + 
                scores.get("Q4", Decimal("0"))) / Decimal("3")
        return base + scores.get("Q5", Decimal("0"))
    
    def get_required_facility_categories(self) -> List[str]:
        return ["通道", "坡道", "出入口", "门", "电梯", "盲道", "其他通行设施",
                "公共卫生间", "无障碍厕所", "公共浴室", "轮椅席位"]
    
    def get_divisor(self) -> int:
        return 3

class StrategyFactory:
    """策略工厂"""
    
    _strategies = {
        BuildingType.RESIDENTIAL: ResidentialStrategy,
        BuildingType.NON_RESIDENTIAL: NonResidentialStrategy,
        BuildingType.PUBLIC_WITH_ACCOM: PublicWithAccomStrategy,
        BuildingType.PUBLIC_NO_ACCOM: PublicNoAccomStrategy,
    }
    
    @classmethod
    def get_strategy(cls, building_type: BuildingType) -> BuildingTypeStrategy:
        strategy_class = cls._strategies.get(building_type)
        if not strategy_class:
            raise ValueError(f"不支持的建筑面积类型: {building_type}")
        return strategy_class()

class ScoringEngine:
    """评分引擎核心"""
    
    @staticmethod
    def check_control_items(control_items: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """Step 1: 控制项闸门检查"""
        for item in control_items:
            if not item.get("is_compliant", False):
                return False, f"控制项 {item.get('clause_id', '未知')} 未达标"
        return True, None
    
    @staticmethod
    def calc_system_score(items: List[ScoreItem]) -> Decimal:
        """Step 2: 系统评分 S 归一化计算"""
        applicable = [i for i in items if i.applicable]
        if not applicable:
            return Decimal("0")
        actual = sum((i.actual_score for i in applicable), Decimal("0"))
        max_sum = sum((i.max_score for i in applicable), Decimal("0"))
        if max_sum == 0:
            return Decimal("0")
        return (actual / max_sum * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calc_facility_score(facility_groups: Dict[str, List[Facility]]) -> Decimal:
        """Step 3: 设施分 F 计算"""
        category_avgs = []
        for category, facilities in facility_groups.items():
            if not facilities:
                continue
            scores = [f.normalized_score for f in facilities]
            category_avg = sum(scores) / len(scores)
            category_avgs.append(category_avg)
        
        if not category_avgs:
            return Decimal("0")
        total = sum(category_avgs) / len(category_avgs)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calc_Qx(system_score: Decimal, facility_score: Decimal) -> Decimal:
        """Step 4: 维度分 Q 计算（Q1/Q2/Q3通用模板）"""
        result = system_score * (facility_score / Decimal("10"))
        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calc_Q4(items: List[ScoreItem]) -> Decimal:
        """Q4 直接评分"""
        return ScoringEngine.calc_system_score(items)
    
    @staticmethod
    def calc_Q5(items: List[ScoreItem], max_score: Decimal = Decimal("20")) -> Decimal:
        """Q5 创新提升加分"""
        total = sum((i.actual_score for i in items if i.applicable), Decimal("0"))
        return min(total, max_score).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @classmethod
    def calc_total_Q(cls, building_type: BuildingType, scores: Dict[str, Decimal]) -> Decimal:
        """Step 5: 总体评价分 Q 计算"""
        strategy = StrategyFactory.get_strategy(building_type)
        result = strategy.get_total_formula(scores)
        return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calc_construction_score(items: List[ScoreItem]) -> Decimal:
        """施工验收评分"""
        return ScoringEngine.calc_system_score(items)
    
    @staticmethod
    def calc_maintenance_score(items: List[ScoreItem]) -> Decimal:
        """运行维护评分"""
        return ScoringEngine.calc_system_score(items)
    
    _GRADE_ORDER = [Grade.NONE, Grade.ONE_STAR, Grade.TWO_STAR, Grade.THREE_STAR]

    @classmethod
    def _aux_score_grade_limit(cls, score: Decimal) -> Grade:
        """施工验收/运行维护分对应的最高可评等级（表2/表3阈值）"""
        if score >= Decimal("80"):
            return Grade.THREE_STAR
        if score >= Decimal("70"):
            return Grade.TWO_STAR
        if score >= Decimal("60"):
            return Grade.ONE_STAR
        return Grade.NONE

    @classmethod
    def determine_grade(
        cls,
        Q: Decimal,
        q1: Decimal,
        q2: Optional[Decimal],
        q3: Optional[Decimal],
        q4: Decimal,
        construction_score: Decimal,
        maintenance_score: Decimal,
        within_one_year: bool,
        site_inspection_passed: Optional[bool] = None
    ) -> tuple[Grade, Dict[str, Any]]:
        """Step 7: 等级认定（依据表2竣工一年内 / 表3竣工一年后）"""
        # 检查各维度最低分要求
        dimension_scores = [q1, q4]
        if q2 is not None:
            dimension_scores.append(q2)
        if q3 is not None:
            dimension_scores.append(q3)

        min_q = min(dimension_scores)

        # 基础等级：各维度最低分 + 总体Q
        if min_q >= Decimal("60") and Q >= Decimal("80"):
            base_grade = Grade.THREE_STAR
        elif min_q >= Decimal("40") and Q >= Decimal("60"):
            base_grade = Grade.TWO_STAR
        elif min_q >= Decimal("20") and Q >= Decimal("40"):
            base_grade = Grade.ONE_STAR
        else:
            return Grade.NONE, {"reason": "未达到一星级最低要求"}

        # 运行维护分两个表均要求；施工验收分仅竣工一年内（表2）要求
        limits = [cls._aux_score_grade_limit(maintenance_score)]
        if within_one_year:
            limits.append(cls._aux_score_grade_limit(construction_score))
        elif site_inspection_passed is not True:
            # 表3：竣工一年后须按GB50642现场检测合格
            return Grade.NONE, {
                "reason": "竣工验收一年后评价须现场检测合格（site_inspection_passed）",
                "total_Q": float(Q),
                "min_dimension_score": float(min_q),
            }

        order = cls._GRADE_ORDER
        grade = min([base_grade] + limits, key=order.index)

        breakdown = {
            "total_Q": float(Q),
            "min_dimension_score": float(min_q),
            "base_grade": base_grade.value,
            "construction_score": float(construction_score),
            "maintenance_score": float(maintenance_score),
            "within_one_year": within_one_year,
        }
        if not within_one_year:
            breakdown["site_inspection_passed"] = site_inspection_passed

        return grade, breakdown
    
    @classmethod
    def calc_complex_full(cls, buildings: List[Dict[str, Any]], z2: Optional[Decimal] = None,
                          within_one_year: bool = True,
                          site_inspection_passed: Optional[bool] = None) -> Dict[str, Any]:
        """建筑群完整综合评价（4.2.1.10）

        buildings: [{id, name, Q, floor_area, q1..q4, construction, maintenance}]
        - 前提：每个单体 Q≥40
        - Z1 = 面积加权平均Q；Q1-Q4/施工验收/运行维护同样按面积加权（不参评维度的建筑不参与该维度加权）
        - Z2 = 整体区域无障碍通行评分（未提供默认80）
        - ZQ = Z1×80% + Z2×20%，按表2/表3确定建筑群等级
        """
        for b in buildings:
            if b.get("Q", Decimal("0")) < Decimal("40"):
                raise ValueError(f"建筑 {b.get('name', '未知')} Q < 40，不满足建筑群整体评价前提")

        total_area = sum(b.get("floor_area", Decimal("0")) for b in buildings)
        if total_area == 0:
            raise ValueError("总建筑面积不能为0")

        Z1 = sum(b["Q"] * b.get("floor_area", Decimal("0")) / total_area for b in buildings)

        def weighted(field: str) -> Optional[Decimal]:
            vals = [(b[field], b.get("floor_area", Decimal("0"))) for b in buildings
                    if b.get(field) is not None]
            if not vals:
                return None
            area_sum = sum(a for _, a in vals)
            if area_sum == 0:
                return None
            return sum(v * a / area_sum for v, a in vals)

        dims = {
            "q1": weighted("q1"), "q2": weighted("q2"), "q3": weighted("q3"), "q4": weighted("q4"),
            "construction": weighted("construction"), "maintenance": weighted("maintenance"),
        }

        Z2 = z2 if z2 is not None else Decimal("80")
        ZQ = Z1 * Decimal("0.8") + Z2 * Decimal("0.2")

        grade, breakdown = cls.determine_grade(
            Q=ZQ,
            q1=dims["q1"] or Decimal("0"),
            q2=dims["q2"],
            q3=dims["q3"],
            q4=dims["q4"] or Decimal("0"),
            construction_score=dims["construction"] or Decimal("0"),
            maintenance_score=dims["maintenance"] or Decimal("0"),
            within_one_year=within_one_year,
            site_inspection_passed=site_inspection_passed,
        )

        building_scores = {
            b.get("id", ""): {
                "name": b.get("name", ""),
                "Q": float(b.get("Q", Decimal("0"))),
                "floor_area": float(b.get("floor_area", Decimal("0"))),
                "weight": float((b.get("floor_area", Decimal("0")) / total_area).quantize(
                    Decimal("0.0001"), rounding=ROUND_HALF_UP))
            }
            for b in buildings
        }

        q = lambda v: v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if v is not None else None
        return {
            "z1": q(Z1), "z2": q(Z2), "zq": q(ZQ),
            "dimensions": {k: q(v) for k, v in dims.items()},
            "grade": grade, "breakdown": breakdown,
            "building_scores": building_scores,
        }

    @staticmethod
    def calc_complex_building_score(buildings: List[Dict[str, Any]], z2: Optional[Decimal] = None) -> tuple[Decimal, Decimal, Decimal, Dict]:
        """建筑群综合评分（4.2.1.10）

        z2: 整体建筑区域无障碍通行评分（按4.2.1.6计算，单体建筑出入口及内部交通不参评），
            未提供时使用默认值80。
        """
        # 检查前提条件
        for b in buildings:
            if b.get("Q", Decimal("0")) < Decimal("40"):
                raise ValueError(f"建筑 {b.get('name', '未知')} Q < 40，不满足建筑群整体评价前提")
        
        # 计算 Z1（单体建筑加权平均）
        total_area = sum(b.get("floor_area", Decimal("0")) for b in buildings)
        if total_area == 0:
            raise ValueError("总建筑面积不能为0")
        
        Z1 = sum(
            b.get("Q", Decimal("0")) * b.get("floor_area", Decimal("0")) / total_area 
            for b in buildings
        )
        
        # Z2 场地通行评分（按4.2.1.6对整体建筑区域评分，未提供时用默认值）
        Z2 = z2 if z2 is not None else Decimal("80")
        
        ZQ = Z1 * Decimal("0.8") + Z2 * Decimal("0.2")
        
        building_scores = {
            b.get("id", ""): {
                "name": b.get("name", ""),
                "Q": b.get("Q", Decimal("0")),
                "floor_area": b.get("floor_area", Decimal("0")),
                "weight": b.get("floor_area", Decimal("0")) / total_area
            }
            for b in buildings
        }
        
        return (
            Z1.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            Z2.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            ZQ.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            building_scores
        )