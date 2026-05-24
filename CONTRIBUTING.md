# Contributing to buildcost

## Setup

```bash
git clone https://github.com/MukundaKatta/buildcost.git
cd buildcost
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest -v
```

## Recalibrating the cost data

The unit costs in `src/buildcost/estimator/materials.py` and the hourly
rates in `src/buildcost/estimator/labor.py` are 2024-2025 US averages.
If you want different units, ranges, or regional multipliers, edit those
files and add a test in `tests/test_residential.py` that pins your
expected output ranges.

The quantity factors in `src/buildcost/estimator/calculator.py`
(`QUANTITY_FACTORS`, `LABOR_HOURS_PER_SQFT`, `EQUIPMENT_RATES`) are where
the residential path is calibrated. Only the `RESIDENTIAL` entry is
ground-truthed; the other four are first-pass placeholders.

## Pull requests

1. Fork and create a feature branch.
2. Write tests for new behavior in `tests/`.
3. Run `pytest` and make sure all tests pass.
4. Update `CHANGELOG.md` under an `Unreleased` section.
5. Open the PR with a short description of what you changed and why.

## License

MIT. By contributing, you agree your contribution is released under MIT.
