# BuildCost - Construction Cost Estimator

A comprehensive construction cost estimation tool that calculates material, labor, and equipment costs organized by CSI MasterFormat divisions.

## Features

- **Cost Calculation**: Compute material, labor, and equipment costs per trade
- **Material Database**: 100+ real construction materials with unit costs
- **Labor Rate Database**: Hourly rates by trade and region
- **CSI MasterFormat Breakdown**: Costs organized by 16 CSI divisions (site work, concrete, masonry, metals, wood, thermal, doors/windows, finishes, mechanical, electrical, plumbing, etc.)
- **Cost Comparison**: Compare estimates against industry benchmarks
- **Contingency Calculation**: Add risk-based contingencies by project type
- **Rich Reports**: Generate detailed cost breakdowns with formatted tables

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Create a cost estimate
buildcost estimate --sqft 2500 --type residential --stories 2 --region southeast

# Get material costs
buildcost materials --search "lumber"

# Compare estimate to benchmarks
buildcost compare --sqft 2500 --type residential --region southeast

# Generate full report
buildcost report --sqft 2500 --type residential --stories 2 --output report.json
```

### Python API

```python
from buildcost.estimator.calculator import CostCalculator
from buildcost.analyzer.breakdown import CostBreakdown

calculator = CostCalculator()
estimate = calculator.estimate(
    square_footage=2500,
    project_type="residential",
    stories=2,
    region="southeast",
)
print(f"Total Cost: ${estimate.total_cost:,.2f}")
```

## Project Structure

```
src/buildcost/
  cli.py              - CLI interface using Click
  models.py           - Pydantic data models
  report.py           - Report generation
  estimator/
    calculator.py     - CostCalculator
    materials.py      - MaterialDatabase (100+ materials)
    labor.py          - LaborRateDatabase
  analyzer/
    breakdown.py      - CostBreakdown by CSI division
    comparator.py     - CostComparator
    contingency.py    - ContingencyCalculator
```

## CSI MasterFormat Divisions

1. General Requirements
2. Site Construction
3. Concrete
4. Masonry
5. Metals
6. Wood, Plastics, Composites
7. Thermal & Moisture Protection
8. Openings (Doors & Windows)
9. Finishes
10. Specialties
11. Equipment
12. Furnishings
13. Special Construction
14. Conveying Equipment
15. Mechanical (HVAC)
16. Electrical

## Dependencies

- numpy - Numerical computations
- pydantic - Data validation and models
- click - CLI framework
- rich - Terminal formatting and tables

## Author

Mukunda Katta

## License

MIT
