"""Cost comparator comparing estimates against industry benchmarks.

Provides comparison of cost estimates against per-square-foot benchmarks
for different project types, regions, and quality levels.
"""

from __future__ import annotations

import numpy as np

from buildcost.models import CostEstimate, ProjectType, Region


# Industry benchmark costs per square foot (2024-2025 averages)
COST_PER_SQFT_BENCHMARKS: dict[ProjectType, dict[str, float]] = {
    ProjectType.RESIDENTIAL: {
        "economy": 125.00,
        "standard": 175.00,
        "premium": 250.00,
        "luxury": 400.00,
    },
    ProjectType.COMMERCIAL: {
        "economy": 150.00,
        "standard": 225.00,
        "premium": 350.00,
        "luxury": 550.00,
    },
    ProjectType.INDUSTRIAL: {
        "economy": 80.00,
        "standard": 125.00,
        "premium": 200.00,
        "luxury": 300.00,
    },
    ProjectType.INSTITUTIONAL: {
        "economy": 200.00,
        "standard": 300.00,
        "premium": 450.00,
        "luxury": 650.00,
    },
    ProjectType.RENOVATION: {
        "economy": 75.00,
        "standard": 150.00,
        "premium": 250.00,
        "luxury": 400.00,
    },
}

# Regional adjustment factors for benchmarks
REGIONAL_BENCHMARK_FACTORS: dict[Region, float] = {
    Region.NORTHEAST: 1.20,
    Region.SOUTHEAST: 0.92,
    Region.MIDWEST: 0.95,
    Region.SOUTHWEST: 1.02,
    Region.WEST: 1.28,
    Region.NORTHWEST: 1.12,
}


class CostComparator:
    """Compares cost estimates against industry benchmarks and other estimates."""

    def compare_to_benchmark(self, estimate: CostEstimate) -> dict:
        """Compare an estimate's cost per sqft against benchmarks.

        Returns comparison results with quality tier classification.
        """
        benchmarks = COST_PER_SQFT_BENCHMARKS.get(
            estimate.project_type,
            COST_PER_SQFT_BENCHMARKS[ProjectType.RESIDENTIAL],
        )
        regional_factor = REGIONAL_BENCHMARK_FACTORS.get(estimate.region, 1.0)

        adjusted_benchmarks = {
            tier: round(cost * regional_factor, 2)
            for tier, cost in benchmarks.items()
        }

        cost_per_sqft = estimate.cost_per_sqft

        # Determine quality tier
        if cost_per_sqft <= adjusted_benchmarks["economy"]:
            tier = "economy"
            position = "below economy"
        elif cost_per_sqft <= adjusted_benchmarks["standard"]:
            tier = "standard"
            position = "economy to standard"
        elif cost_per_sqft <= adjusted_benchmarks["premium"]:
            tier = "premium"
            position = "standard to premium"
        elif cost_per_sqft <= adjusted_benchmarks["luxury"]:
            tier = "luxury"
            position = "premium to luxury"
        else:
            tier = "ultra_luxury"
            position = "above luxury"

        # Calculate variance from standard
        standard = adjusted_benchmarks["standard"]
        variance_pct = ((cost_per_sqft - standard) / standard) * 100

        return {
            "cost_per_sqft": round(cost_per_sqft, 2),
            "quality_tier": tier,
            "position": position,
            "benchmarks": adjusted_benchmarks,
            "region": estimate.region.value,
            "regional_factor": regional_factor,
            "variance_from_standard_pct": round(variance_pct, 1),
            "is_within_normal_range": -15 <= variance_pct <= 30,
        }

    def compare_estimates(
        self, estimate_a: CostEstimate, estimate_b: CostEstimate,
    ) -> dict:
        """Compare two cost estimates side by side."""
        diff_total = estimate_a.total_cost - estimate_b.total_cost
        diff_pct = (diff_total / estimate_b.total_cost * 100) if estimate_b.total_cost else 0

        return {
            "estimate_a": {
                "name": estimate_a.project_name,
                "total_cost": round(estimate_a.total_cost, 2),
                "cost_per_sqft": round(estimate_a.cost_per_sqft, 2),
                "sqft": estimate_a.square_footage,
            },
            "estimate_b": {
                "name": estimate_b.project_name,
                "total_cost": round(estimate_b.total_cost, 2),
                "cost_per_sqft": round(estimate_b.cost_per_sqft, 2),
                "sqft": estimate_b.square_footage,
            },
            "difference_total": round(diff_total, 2),
            "difference_pct": round(diff_pct, 1),
            "cheaper": "a" if diff_total < 0 else "b",
        }

    def get_regional_comparison(
        self, square_footage: float, project_type: ProjectType,
    ) -> dict[str, dict]:
        """Compare estimated costs across all regions."""
        benchmarks = COST_PER_SQFT_BENCHMARKS.get(
            project_type, COST_PER_SQFT_BENCHMARKS[ProjectType.RESIDENTIAL],
        )
        standard = benchmarks["standard"]

        results = {}
        for region in Region:
            factor = REGIONAL_BENCHMARK_FACTORS.get(region, 1.0)
            adjusted_cost = standard * factor
            results[region.value] = {
                "cost_per_sqft": round(adjusted_cost, 2),
                "estimated_total": round(adjusted_cost * square_footage, 2),
                "regional_factor": factor,
            }

        return results

    def analyze_cost_drivers(self, estimate: CostEstimate) -> list[dict]:
        """Identify the top cost drivers in an estimate."""
        if not estimate.line_items:
            return []

        sorted_items = sorted(estimate.line_items, key=lambda x: x.total_cost, reverse=True)
        total = estimate.subtotal

        drivers = []
        for item in sorted_items[:10]:
            drivers.append({
                "description": item.description,
                "total_cost": round(item.total_cost, 2),
                "percentage": round((item.total_cost / total) * 100, 1) if total else 0,
                "division": item.csi_division.value,
                "category": item.category,
            })

        return drivers
