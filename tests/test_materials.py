"""Tests for material database."""

import pytest
from buildcost.estimator.materials import MaterialDatabase
from buildcost.models import CSIDivision


@pytest.fixture
def db():
    return MaterialDatabase()


class TestMaterialDatabase:
    def test_has_100_plus_materials(self, db):
        assert db.count() >= 100

    def test_search_lumber(self, db):
        results = db.search("lumber")
        assert len(results) >= 1
        assert any("Lumber" in m.name for m in results)

    def test_search_concrete(self, db):
        results = db.search("concrete")
        assert len(results) >= 3

    def test_search_case_insensitive(self, db):
        results_upper = db.search("PLYWOOD")
        results_lower = db.search("plywood")
        assert len(results_upper) == len(results_lower)

    def test_get_by_name(self, db):
        m = db.get_by_name("Ready-Mix Concrete 3000 PSI")
        assert m is not None
        assert m.unit_cost == 145.00

    def test_get_by_name_not_found(self, db):
        assert db.get_by_name("NonExistent Material") is None

    def test_get_by_division(self, db):
        concrete_mats = db.get_by_division(CSIDivision.DIV_03_CONCRETE)
        assert len(concrete_mats) >= 3

    def test_get_by_category(self, db):
        roofing = db.get_by_category("roofing")
        assert len(roofing) >= 2

    def test_all_materials_have_positive_cost(self, db):
        for m in db.materials:
            assert m.unit_cost > 0, f"{m.name} has non-positive cost"

    def test_list_categories(self, db):
        cats = db.list_categories()
        assert len(cats) >= 10
        assert "concrete" in cats

    def test_list_divisions(self, db):
        divs = db.list_divisions()
        assert len(divs) >= 8

    def test_multiple_divisions_covered(self, db):
        """Ensure materials span multiple CSI divisions."""
        divisions_with_materials = set()
        for m in db.materials:
            divisions_with_materials.add(m.csi_division)
        assert len(divisions_with_materials) >= 8
