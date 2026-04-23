"""Cost breakdown by CSI MasterFormat divisions.

Provides detailed analysis of costs organized by the 16 CSI divisions
used throughout the construction industry.
"""

from __future__ import annotations

from buildcost.models import CostEstimate, CSIDivision


# Industry benchmark percentages by CSI division for residential construction
RESIDENTIAL_BENCHMARKS: dict[CSIDivision, float] = {
    CSIDivision.DIV_01_GENERAL: 8.0,
    CSIDivision.DIV_02_SITE: 6.0,
    CSIDivision.DIV_03_CONCRETE: 10.0,
    CSIDivision.DIV_04_MASONRY: 3.0,
    CSIDivision.DIV_05_METALS: 2.0,
    CSIDivision.DIV_06_WOOD: 14.0,
    CSIDivision.DIV_07_THERMAL: 8.0,
    CSIDivision.DIV_08_OPENINGS: 6.0,
    CSIDivision.DIV_09_FINISHES: 15.0,
    CSIDivision.DIV_10_SPECIALTIES: 1.5,
    CSIDivision.DIV_11_EQUIPMENT: 1.0,
    CSIDivision.DIV_12_FURNISHINGS: 1.5,
    CSIDivision.DIV_13_SPECIAL: 0.5,
    CSIDivision.DIV_14_CONVEYING: 0.5,
    CSIDivision.DIV_15_MECHANICAL: 14.0,
    CSIDivision.DIV_16_ELECTRICAL: 9.0,
}

COMMERCIAL_BENCHMARKS: dict[CSIDivision, float] = {
    CSIDivision.DIV_01_GENERAL: 10.0,
    CSIDivision.DIV_02_SITE: 5.0,
    CSIDivision.DIV_03_CONCRETE: 12.0,
    CSIDivision.DIV_04_MASONRY: 4.0,
    CSIDivision.DIV_05_METALS: 8.0,
    CSIDivision.DIV_06_WOOD: 5.0,
    CSIDivision.DIV_07_THERMAL: 7.0,
    CSIDivision.DIV_08_OPENINGS: 7.0,
    CSIDivision.DIV_09_FINISHES: 12.0,
    CSIDivision.DIV_10_SPECIALTIES: 2.0,
    CSIDivision.DIV_11_EQUIPMENT: 2.0,
    CSIDivision.DIV_12_FURNISHINGS: 2.0,
    CSIDivision.DIV_13_SPECIAL: 1.0,
    CSIDivision.DIV_14_CONVEYING: 3.0,
    CSIDivision.DIV_15_MECHANICAL: 12.0,
    CSIDivision.DIV_16_ELECTRICAL: 8.0,
}


class CostBreakdown:
    """Analyzes cost estimates by CSI MasterFormat divisions.

    Provides:
    - Division-level cost summaries
    - Material/labor/equipment splits
    - Percentage breakdowns
    - Variance from industry benchmarks
    """

    def get_division_breakdown(self, estimate: CostEstimate) -> list[dict]:
        """Get a detailed breakdown by CSI division.

        Returns a list of dicts with division name, costs, and percentages.
        """
        subtotal = estimate.subtotal
        if subtotal == 0:
            return []

        breakdown = []
        for dc in estimate.division_costs:
            breakdown.append({
                "division": dc.division.value,
                "material_cost": round(dc.material_cost, 2),
                "labor_cost": round(dc.labor_cost, 2),
                "equipment_cost": round(dc.equipment_cost, 2),
                "total_cost": round(dc.total_cost, 2),
                "percentage": round((dc.total_cost / subtotal) * 100, 1),
                "line_item_count": len(dc.line_items),
            })

        breakdown.sort(key=lambda x: x["total_cost"], reverse=True)
        return breakdown

    def get_cost_split(self, estimate: CostEstimate) -> dict:
        """Get the material/labor/equipment cost split."""
        subtotal = estimate.subtotal
        if subtotal == 0:
            return {"material_pct": 0, "labor_pct": 0, "equipment_pct": 0}

        return {
            "material_cost": round(estimate.subtotal_material, 2),
            "labor_cost": round(estimate.subtotal_labor, 2),
            "equipment_cost": round(estimate.subtotal_equipment, 2),
            "material_pct": round((estimate.subtotal_material / subtotal) * 100, 1),
            "labor_pct": round((estimate.subtotal_labor / subtotal) * 100, 1),
            "equipment_pct": round((estimate.subtotal_equipment / subtotal) * 100, 1),
        }

    def get_top_cost_divisions(self, estimate: CostEstimate, n: int = 5) -> list[dict]:
        """Get the top N most expensive divisions."""
        breakdown = self.get_division_breakdown(estimate)
        return breakdown[:n]

    def get_cost_per_sqft_by_division(self, estimate: CostEstimate) -> dict[str, float]:
        """Get cost per square foot for each division."""
        result = {}
        for dc in estimate.division_costs:
            result[dc.division.value] = round(dc.total_cost / estimate.square_footage, 2)
        return result

    def get_benchmark_comparison(self, estimate: CostEstimate) -> list[dict]:
        """Compare estimate percentages against industry benchmarks."""
        from buildcost.models import ProjectType

        benchmarks = (
            COMMERCIAL_BENCHMARKS
            if estimate.project_type == ProjectType.COMMERCIAL
            else RESIDENTIAL_BENCHMARKS
        )

        subtotal = estimate.subtotal
        if subtotal == 0:
            return []

        # Build lookup of actual percentages
        actual: dict[CSIDivision, float] = {}
        for dc in estimate.division_costs:
            actual[dc.division] = (dc.total_cost / subtotal) * 100

        comparisons = []
        for div in CSIDivision:
            bench = benchmarks.get(div, 0)
            act = actual.get(div, 0)
            variance = act - bench
            comparisons.append({
                "division": div.value,
                "benchmark_pct": bench,
                "actual_pct": round(act, 1),
                "variance_pct": round(variance, 1),
                "status": "over" if variance > 2 else ("under" if variance < -2 else "normal"),
            })

        return comparisons
