# Changelog

## v0.2.0 - 2026-05-24

Revival release. The March scaffold was a generic, "AI-powered" stub
sitting on top of a half-built construction cost engine. This release
narrows scope to a single calibrated path and makes it actually work.

### Added

- Calibrated end-to-end residential cost estimate using the existing
  material, labor, contingency, and analyzer modules.
- `examples/estimate_residential.py`: one runnable example that estimates
  a 2,400 sqft single-story SE home and prints the CSI breakdown, cost
  split, top cost drivers, and a benchmark check.
- `tests/test_residential.py`: 15 tests that pin the residential dollar
  range, labor-vs-material split, division coverage, contingency share,
  determinism, and edge cases.
- `tests/test_cli.py`: 8 CLI smoke tests covering `estimate`, `materials`,
  `compare`, `report`, JSON output, version, and help.
- `LICENSE` (MIT) and this `CHANGELOG.md`.

### Changed

- Project scope is now residential-first. Commercial, industrial,
  institutional, and renovation paths are retained for compatibility
  but documented as uncalibrated.
- README rewritten to describe what works, what is calibrated, and what
  is structural-only.
- Fixed `pyproject.toml` build backend (was pointing at a non-existent
  `setuptools.backends._legacy` module).
- License flipped from proprietary to MIT.
- Version bumped to 0.2.0; package description updated.

### Removed

- `src/core.py`: generic `Buildcost` class with 8 noop methods
  (`generate`, `create`, `validate`, `preview`, `export`, `get_templates`,
  `get_stats`, `reset`). It produced `{"ok": True, "service": "buildcost"}`
  for any input and did not touch the actual cost engine.
- `src/processor.py`: generic `DataProcessor` / `Validator` framework that
  was never wired to anything in this project.
- `src/utils.py`: generic `retry`, `SimpleCache`, `sanitize_input`,
  `generate_id` helpers that no real cost code path consumed.
- `src/health.py`: hardcoded `{"status": "ok"}` health endpoint with no
  server attached.
- `src/__main__.py`: stub CLI that just printed `{"ok": True}`. The real
  CLI lives at `buildcost.cli` and is exposed through the `buildcost`
  entry point in `pyproject.toml`.
- `tests/test_core.py`, `tests/test_integration.py`, `tests/test_benchmark.py`,
  `tests/test_utils.py`: 33 tests that exercised the stub paths above.
  Removing them lost no real coverage; the remaining 60 tests already
  exercise the actual engine, and the new 23 add residential and CLI
  coverage.
- `examples/basic.py`, `examples/advanced.py`: stub demos that called the
  noop `Buildcost` class. The `basic.py` example also had a Python syntax
  error (`"validate]` instead of `"validate"]`) that would have crashed
  it. Replaced with `examples/estimate_residential.py`.
- `config.example.yaml` and `.env.example`: served the stub and were never
  read by any module.
- `numpy` dependency. It was imported by three files
  (`calculator.py`, `breakdown.py`, `comparator.py`) and never used.

## v0.1.0 - 2026-03-18

Initial scaffold (now archived in git history). Included a generic
`Buildcost` stub class, a real-but-disconnected construction estimator
package (calculator, materials, labor, analyzer, contingency, report,
CLI), an "AI-powered blueprint analyzer" README that was aspirational, and
84 tests of which 33 exercised the stub.
