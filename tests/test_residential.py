"""End-to-end tests for the calibrated residential path.

Residential is the project type buildcost is calibrated against. These
tests pin the numbers in a range that matches 2024-2025 US single-family
home construction averages, so regressions are visible if the cost
assumptions drift.
"""

from __future__ import annotations

import pytest

from buildcost.analyzer.breakdown import CostBreakdown
from buildcost.analyzer.comparator import CostComparator
from buildcost.estimator.calculator import CostCalculator
from buildcost.models import CSIDivision, ProjectType, Region
from buildcost.report import CostReportGenerator


@pytest.fixture
def estimate_2400_sqft_southeast():
    """A canonical 2,400 sqft single-story residential estimate in the SE."""
    calc = CostCalculator()
    return calc.estimate(
        square_footage=2400,
        project_type="residential",
        stories=1,
        region="southeast",
        project_name="Sample Single-Family Home",
        include_contingency=True,
    )


class TestResidentialEndToEnd:
    def test_total_cost_in_realistic_range(self, estimate_2400_sqft_southeast):
        # 2,400 sqft SE residential should land between $300K and $700K
        # (covers standard to premium quality tiers after contingency).
        est = estimate_2400_sqft_southeast
        assert 300_000 < est.total_cost < 700_000

    def test_cost_per_sqft_is_typical_residential(self, estimate_2400_sqft_southeast):
        est = estimate_2400_sqft_southeast
        # SE residential typical range is roughly $130-$300/sqft
        # including standard contingency.
        assert 130 < est.cost_per_sqft < 300

    def test_labor_dominates_residential_cost(self, estimate_2400_sqft_southeast):
        """Residential builds are usually 50-80% labor."""
        est = estimate_2400_sqft_southeast
        labor_pct = (est.subtotal_labor / est.subtotal) * 100
        assert 50 < labor_pct < 85

    def test_wood_division_is_top_three(self, estimate_2400_sqft_southeast):
        """Wood framing is one of the largest residential cost drivers."""
        breakdown = CostBreakdown()
        top = breakdown.get_top_cost_divisions(estimate_2400_sqft_southeast, n=3)
        top_names = [t["division"] for t in top]
        assert any("Wood" in name for name in top_names)

    def test_estimate_has_all_expected_residential_divisions(
        self, estimate_2400_sqft_southeast,
    ):
        """A residential estimate must cover the core CSI divisions."""
        est = estimate_2400_sqft_southeast
        divs_present = {dc.division for dc in est.division_costs if dc.total_cost > 0}
        required = {
            CSIDivision.DIV_02_SITE,
            CSIDivision.DIV_03_CONCRETE,
            CSIDivision.DIV_06_WOOD,
            CSIDivision.DIV_07_THERMAL,
            CSIDivision.DIV_09_FINISHES,
            CSIDivision.DIV_15_MECHANICAL,
            CSIDivision.DIV_16_ELECTRICAL,
        }
        missing = required - divs_present
        assert not missing, f"Missing required residential divisions: {missing}"

    def test_contingency_is_meaningful_share(self, estimate_2400_sqft_southeast):
        """Default residential contingency should be 12-25% of subtotal."""
        est = estimate_2400_sqft_southeast
        pct = (est.contingency_total / est.subtotal) * 100
        assert 12 < pct < 25

    def test_benchmark_classifies_into_known_tier(self, estimate_2400_sqft_southeast):
        comp = CostComparator()
        result = comp.compare_to_benchmark(estimate_2400_sqft_southeast)
        assert result["quality_tier"] in (
            "economy", "standard", "premium", "luxury", "ultra_luxury",
        )

    def test_estimate_is_deterministic(self):
        """Calling the calculator twice with the same input must give the same total."""
        calc = CostCalculator()
        a = calc.estimate(square_footage=2400, project_type="residential", region="southeast")
        b = calc.estimate(square_footage=2400, project_type="residential", region="southeast")
        assert a.total_cost == b.total_cost
        assert a.subtotal == b.subtotal

    def test_doubling_sqft_roughly_doubles_cost(self):
        """Cost should scale roughly linearly with sqft for residential."""
        calc = CostCalculator()
        small = calc.estimate(square_footage=1500, project_type="residential")
        big = calc.estimate(square_footage=3000, project_type="residential")
        ratio = big.total_cost / small.total_cost
        # Allow some non-linearity for fixed items (water heater, panel, etc.)
        assert 1.7 < ratio < 2.3

    def test_report_generator_outputs_json(self, estimate_2400_sqft_southeast):
        """The report generator must export to a parseable JSON string."""
        import json

        gen = CostReportGenerator()
        payload = gen.to_json(estimate_2400_sqft_southeast)
        parsed = json.loads(payload)
        assert parsed["project_name"] == "Sample Single-Family Home"
        assert parsed["total_cost"] > 0
        assert len(parsed["line_items"]) > 20


class TestResidentialEdgeCases:
    def test_zero_sqft_rejected(self):
        calc = CostCalculator()
        with pytest.raises(Exception):
            calc.estimate(square_footage=0, project_type="residential")

    def test_negative_sqft_rejected(self):
        calc = CostCalculator()
        with pytest.raises(Exception):
            calc.estimate(square_footage=-100, project_type="residential")

    def test_tiny_house_still_produces_estimate(self):
        """A 400 sqft tiny home should still get a valid estimate."""
        calc = CostCalculator()
        est = calc.estimate(square_footage=400, project_type="residential")
        assert est.total_cost > 0
        # Minimum panel, water heater, etc., still appear.
        assert any(
            "Electrical Panel" in li.description for li in est.line_items
        )

    def test_unknown_project_type_rejected(self):
        calc = CostCalculator()
        with pytest.raises(ValueError):
            calc.estimate(square_footage=2000, project_type="airplane")

    def test_unknown_region_rejected(self):
        calc = CostCalculator()
        with pytest.raises(ValueError):
            calc.estimate(square_footage=2000, region="atlantis")
