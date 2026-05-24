"""End-to-end residential estimate demo.

Estimates a 2,400 sqft single-story residential house in the Southeast,
then prints the full CSI MasterFormat breakdown, the cost split between
material/labor/equipment, the top cost drivers, and a benchmark check
against the standard residential cost-per-square-foot tier.

Run:
    python examples/estimate_residential.py
"""

from __future__ import annotations

from buildcost.analyzer.breakdown import CostBreakdown
from buildcost.analyzer.comparator import CostComparator
from buildcost.estimator.calculator import CostCalculator
from buildcost.report import CostReportGenerator


SQFT = 2400
PROJECT_NAME = "Sample Single-Family Home"
PROJECT_TYPE = "residential"
REGION = "southeast"
STORIES = 1


def main() -> None:
    calculator = CostCalculator()
    estimate = calculator.estimate(
        square_footage=SQFT,
        project_type=PROJECT_TYPE,
        stories=STORIES,
        region=REGION,
        project_name=PROJECT_NAME,
        include_contingency=True,
    )

    reporter = CostReportGenerator()
    reporter.print_full_report(estimate)

    # Add the analyzer outputs to show the engine is not just a printer.
    breakdown = CostBreakdown()
    split = breakdown.get_cost_split(estimate)
    print()
    print("Cost split:")
    print(f"  Materials: ${split['material_cost']:>12,.2f} ({split['material_pct']:.1f}%)")
    print(f"  Labor:     ${split['labor_cost']:>12,.2f} ({split['labor_pct']:.1f}%)")
    print(f"  Equipment: ${split['equipment_cost']:>12,.2f} ({split['equipment_pct']:.1f}%)")

    top = breakdown.get_top_cost_divisions(estimate, n=3)
    print()
    print("Top 3 cost divisions:")
    for row in top:
        print(f"  {row['division']:<40} ${row['total_cost']:>12,.2f}  ({row['percentage']:.1f}%)")

    comparator = CostComparator()
    bench = comparator.compare_to_benchmark(estimate)
    print()
    print("Benchmark check:")
    print(f"  Your cost per sqft: ${bench['cost_per_sqft']:.2f}")
    print(f"  Quality tier:       {bench['quality_tier']}")
    print(f"  Region-adjusted standard benchmark: ${bench['benchmarks']['standard']:.2f}/sqft")
    print(f"  Variance from standard:             {bench['variance_from_standard_pct']:+.1f}%")
    print(f"  Within normal range:                {bench['is_within_normal_range']}")


if __name__ == "__main__":
    main()
