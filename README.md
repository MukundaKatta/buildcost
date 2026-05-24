# buildcost

Residential construction cost estimator with CSI MasterFormat breakdown.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Tests](https://img.shields.io/badge/tests-83%20passing-brightgreen)

## What it does

Given a residential square footage, region, and number of stories, buildcost
produces a single-family construction cost estimate broken down by the 16
CSI MasterFormat divisions. It also computes a region-aware comparison to
standard $/sqft tiers (economy / standard / premium / luxury), surfaces the
top cost drivers, and adds the usual risk contingencies (price volatility,
design changes, weather, permits).

The numbers are not a quote. They are a sanity check for a homeowner,
contractor, or architect doing back-of-the-envelope work, with the data
sources tied to 2024-2025 US averages.

## Scope (be honest about this)

Calibrated:

- `residential` single-family, 1-3 stories, all 6 US regions

Retained but uncalibrated (do not trust the absolute dollar values for these,
the structure works but the quantity factors are first-pass only):

- `commercial`
- `industrial`
- `institutional`
- `renovation`

If you need accurate non-residential numbers, fork it and recalibrate the
`QUANTITY_FACTORS` and `LABOR_HOURS_PER_SQFT` tables in
`src/buildcost/estimator/calculator.py`.

## Install

```bash
pip install -e ".[dev]"
```

Runtime deps: pydantic, click, rich. No LLM, no API key, no network call.

## Quick start

End-to-end example:

```bash
python examples/estimate_residential.py
```

Or use the CLI:

```bash
buildcost estimate --sqft 2400 --type residential --region southeast --name "2400 sqft home"
buildcost materials --search concrete
buildcost compare --sqft 2400 --type residential --region west
```

Programmatic:

```python
from buildcost.estimator.calculator import CostCalculator
from buildcost.report import CostReportGenerator

calc = CostCalculator()
estimate = calc.estimate(
    square_footage=2400,
    project_type="residential",
    stories=1,
    region="southeast",
    project_name="Sample Single-Family Home",
)

reporter = CostReportGenerator()
reporter.print_full_report(estimate)
```

## What you get back

A `CostEstimate` (pydantic model) with:

- `line_items`: every material, labor, and equipment line
- `division_costs`: aggregated cost per CSI division
- `contingencies`: itemized risk contingencies with reasons
- `subtotal`, `contingency_total`, `total_cost`, `cost_per_sqft`

The cost split for a 2,400 sqft single-story SE home looks like:

```
Materials: $97,703.95  (22.3%)
Labor:     $331,581.60 (75.6%)
Equipment: $9,324.00   (2.1%)
```

This labor-heavy split matches industry norms for residential builds.

## How it works

1. `MaterialDatabase` ships with ~120 materials tagged to CSI divisions with
   unit costs and waste factors (`src/buildcost/estimator/materials.py`).
2. `LaborRateDatabase` ships with ~25 trade hourly rates plus regional
   multipliers (`src/buildcost/estimator/labor.py`).
3. `CostCalculator` applies industry-standard quantity-per-sqft factors,
   labor-hours-per-sqft factors, and equipment days, then bills against the
   two databases.
4. `ContingencyCalculator` adds 6 risk-based contingency line items
   (base, multi-story, market volatility, design changes, weather, permits).
5. `CostBreakdown` and `CostComparator` analyze the resulting estimate and
   compare against industry tier benchmarks.

All steps run locally. There is no model call. The "AI-powered" framing in
the original March scaffold was aspirational and has been removed.

## Tests

```bash
pytest -v
```

83 tests cover the calculator, materials and labor databases, analyzers,
contingencies, CLI smoke flow, and a calibrated residential end-to-end suite
that pins the realistic dollar range and labor/material split.

## License

MIT. See [LICENSE](./LICENSE).
