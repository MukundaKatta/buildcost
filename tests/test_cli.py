"""Smoke tests for the buildcost CLI.

These verify the CLI entry point wires correctly to the calculator and
prints something sensible. They are not a substitute for the calculator
tests; they protect the user-facing contract.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from buildcost.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "estimate" in result.output
        assert "materials" in result.output

    def test_estimate_residential_2400(self, runner):
        result = runner.invoke(cli, [
            "estimate", "--sqft", "2400",
            "--type", "residential",
            "--region", "southeast",
            "--name", "Test Home",
        ])
        assert result.exit_code == 0
        assert "Test Home" in result.output
        assert "TOTAL ESTIMATED COST" in result.output

    def test_estimate_writes_json(self, runner):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            result = runner.invoke(cli, [
                "estimate", "--sqft", "2400",
                "--type", "residential",
                "--output", str(out),
            ])
            assert result.exit_code == 0
            assert out.exists()
            payload = json.loads(out.read_text())
            assert payload["total_cost"] > 0

    def test_materials_lists_db(self, runner):
        result = runner.invoke(cli, ["materials"])
        assert result.exit_code == 0
        assert "Total materials in database" in result.output

    def test_materials_search(self, runner):
        result = runner.invoke(cli, ["materials", "--search", "concrete"])
        assert result.exit_code == 0
        assert "Concrete" in result.output

    def test_compare_runs(self, runner):
        result = runner.invoke(cli, [
            "compare", "--sqft", "2400", "--type", "residential",
        ])
        assert result.exit_code == 0
        assert "Quality tier" in result.output

    def test_report_runs(self, runner):
        result = runner.invoke(cli, [
            "report", "--sqft", "2400", "--type", "residential",
        ])
        assert result.exit_code == 0
        assert "TOTAL ESTIMATED COST" in result.output
