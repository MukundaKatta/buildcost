"""Tests for cost calculator."""

import pytest
from buildcost.estimator.calculator import CostCalculator
from buildcost.models import ProjectType, Region


@pytest.fixture
def calculator():
    return CostCalculator()


class TestCostCalculator:
    def test_basic_estimate(self, calculator):
        est = calculator.estimate(square_footage=2500)
        assert est.total_cost > 0
        assert est.cost_per_sqft > 0
        assert len(est.line_items) > 0

    def test_estimate_has_materials_and_labor(self, calculator):
        est = calculator.estimate(square_footage=2500)
        assert est.subtotal_material > 0
        assert est.subtotal_labor > 0
        assert est.subtotal_equipment > 0

    def test_larger_home_costs_more(self, calculator):
        small = calculator.estimate(square_footage=1500)
        large = calculator.estimate(square_footage=3000)
        assert large.total_cost > small.total_cost

    def test_multi_story_costs_more(self, calculator):
        one_story = calculator.estimate(square_footage=2500, stories=1)
        two_story = calculator.estimate(square_footage=2500, stories=2)
        assert two_story.total_cost > one_story.total_cost

    def test_different_project_types(self, calculator):
        residential = calculator.estimate(square_footage=2500, project_type="residential")
        commercial = calculator.estimate(square_footage=2500, project_type="commercial")
        assert residential.total_cost != commercial.total_cost

    def test_regional_cost_variation(self, calculator):
        se = calculator.estimate(square_footage=2500, region="southeast")
        ne = calculator.estimate(square_footage=2500, region="northeast")
        assert ne.total_cost > se.total_cost  # NE is more expensive

    def test_division_costs_populated(self, calculator):
        est = calculator.estimate(square_footage=2500)
        assert len(est.division_costs) >= 5

    def test_contingencies_included(self, calculator):
        est = calculator.estimate(square_footage=2500, include_contingency=True)
        assert est.contingency_total > 0
        assert len(est.contingencies) >= 4

    def test_no_contingencies(self, calculator):
        est = calculator.estimate(square_footage=2500, include_contingency=False)
        assert est.contingency_total == 0

    def test_reasonable_cost_per_sqft(self, calculator):
        est = calculator.estimate(square_footage=2500, project_type="residential")
        # Residential should be roughly $100-$400/sqft
        assert 50 < est.cost_per_sqft < 500

    def test_all_project_types(self, calculator):
        for pt in ProjectType:
            est = calculator.estimate(square_footage=2000, project_type=pt.value)
            assert est.total_cost > 0

    def test_all_regions(self, calculator):
        for region in Region:
            est = calculator.estimate(square_footage=2000, region=region.value)
            assert est.total_cost > 0

    def test_estimate_totals_consistent(self, calculator):
        est = calculator.estimate(square_footage=2500)
        assert est.subtotal == pytest.approx(
            est.subtotal_material + est.subtotal_labor + est.subtotal_equipment, rel=0.01,
        )
        assert est.total_cost == pytest.approx(
            est.subtotal + est.contingency_total, rel=0.01,
        )
