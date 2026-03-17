"""Tests for cost analysis modules."""

import pytest
from buildcost.estimator.calculator import CostCalculator
from buildcost.analyzer.breakdown import CostBreakdown
from buildcost.analyzer.comparator import CostComparator
from buildcost.analyzer.contingency import ContingencyCalculator
from buildcost.models import ProjectType, Region


@pytest.fixture
def estimate():
    calc = CostCalculator()
    return calc.estimate(square_footage=2500, project_type="residential", region="southeast")


class TestCostBreakdown:
    def test_division_breakdown(self, estimate):
        breakdown = CostBreakdown()
        result = breakdown.get_division_breakdown(estimate)
        assert len(result) >= 5
        # Percentages should sum near 100
        total_pct = sum(r["percentage"] for r in result)
        assert 95 < total_pct < 105

    def test_cost_split(self, estimate):
        breakdown = CostBreakdown()
        split = breakdown.get_cost_split(estimate)
        assert split["material_pct"] > 0
        assert split["labor_pct"] > 0
        total_pct = split["material_pct"] + split["labor_pct"] + split["equipment_pct"]
        assert 99 < total_pct < 101

    def test_top_cost_divisions(self, estimate):
        breakdown = CostBreakdown()
        top = breakdown.get_top_cost_divisions(estimate, n=3)
        assert len(top) == 3
        # Should be sorted descending by cost
        assert top[0]["total_cost"] >= top[1]["total_cost"]

    def test_cost_per_sqft_by_division(self, estimate):
        breakdown = CostBreakdown()
        result = breakdown.get_cost_per_sqft_by_division(estimate)
        assert len(result) >= 5
        for val in result.values():
            assert val >= 0

    def test_benchmark_comparison(self, estimate):
        breakdown = CostBreakdown()
        result = breakdown.get_benchmark_comparison(estimate)
        assert len(result) == 16  # All CSI divisions
        for item in result:
            assert "benchmark_pct" in item
            assert "actual_pct" in item
            assert "status" in item


class TestCostComparator:
    def test_compare_to_benchmark(self, estimate):
        comp = CostComparator()
        result = comp.compare_to_benchmark(estimate)
        assert "cost_per_sqft" in result
        assert "quality_tier" in result
        assert result["quality_tier"] in ("economy", "standard", "premium", "luxury", "ultra_luxury")

    def test_regional_comparison(self):
        comp = CostComparator()
        result = comp.get_regional_comparison(2500, ProjectType.RESIDENTIAL)
        assert len(result) == 6  # All regions
        assert "southeast" in result
        assert result["west"]["cost_per_sqft"] > result["southeast"]["cost_per_sqft"]

    def test_compare_estimates(self, estimate):
        calc = CostCalculator()
        est2 = calc.estimate(square_footage=3000, project_type="residential")
        comp = CostComparator()
        result = comp.compare_estimates(estimate, est2)
        assert "difference_total" in result
        assert result["cheaper"] == "a"  # Smaller is cheaper

    def test_cost_drivers(self, estimate):
        comp = CostComparator()
        drivers = comp.analyze_cost_drivers(estimate)
        assert len(drivers) == 10
        # First should be most expensive
        assert drivers[0]["total_cost"] >= drivers[1]["total_cost"]


class TestContingencyCalculator:
    def test_basic_contingency(self):
        calc = ContingencyCalculator()
        items = calc.calculate(100000, ProjectType.RESIDENTIAL)
        assert len(items) >= 4
        total = sum(i.amount for i in items)
        assert total > 0

    def test_renovation_higher_contingency(self):
        calc = ContingencyCalculator()
        res = calc.calculate(100000, ProjectType.RESIDENTIAL)
        ren = calc.calculate(100000, ProjectType.RENOVATION)
        res_total = sum(i.amount for i in res)
        ren_total = sum(i.amount for i in ren)
        assert ren_total > res_total

    def test_multi_story_adds_contingency(self):
        calc = ContingencyCalculator()
        one = calc.calculate(100000, ProjectType.RESIDENTIAL, stories=1)
        three = calc.calculate(100000, ProjectType.RESIDENTIAL, stories=3)
        assert sum(i.amount for i in three) > sum(i.amount for i in one)

    def test_total_contingency_pct(self):
        calc = ContingencyCalculator()
        pct = calc.get_total_contingency_pct(ProjectType.RESIDENTIAL)
        assert pct > 10  # Base 8% + extras

    def test_risk_summary(self):
        summary = ContingencyCalculator.get_risk_summary()
        assert "multi_story" in summary
        assert "market_volatility" in summary
