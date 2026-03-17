"""Tests for BuildCost data models."""

import pytest
from buildcost.models import (
    CostEstimate,
    CSIDivision,
    DivisionCost,
    LineItem,
    Material,
    Project,
    ProjectType,
    Region,
    UnitType,
)


class TestMaterial:
    def test_material_creation(self):
        m = Material(
            name="Concrete", category="concrete",
            csi_division=CSIDivision.DIV_03_CONCRETE,
            unit=UnitType.CY, unit_cost=145.00,
        )
        assert m.name == "Concrete"
        assert m.unit_cost == 145.00
        assert m.waste_factor == 0.05

    def test_material_waste_factor(self):
        m = Material(
            name="Tile", category="tile",
            csi_division=CSIDivision.DIV_09_FINISHES,
            unit=UnitType.SQFT, unit_cost=5.50, waste_factor=0.10,
        )
        assert m.waste_factor == 0.10


class TestLineItem:
    def test_line_item_total(self):
        li = LineItem(
            description="Lumber", csi_division=CSIDivision.DIV_06_WOOD,
            quantity=100, unit=UnitType.EA, unit_cost=4.25,
            total_cost=425.00, category="material",
        )
        assert li.computed_total == 425.00

    def test_line_item_categories(self):
        for cat in ["material", "labor", "equipment"]:
            li = LineItem(
                description="Test", csi_division=CSIDivision.DIV_01_GENERAL,
                quantity=1, unit=UnitType.EA, unit_cost=10.00,
                total_cost=10.00, category=cat,
            )
            assert li.category == cat


class TestDivisionCost:
    def test_division_total(self):
        dc = DivisionCost(
            division=CSIDivision.DIV_03_CONCRETE,
            material_cost=5000, labor_cost=3000, equipment_cost=1000,
        )
        assert dc.total_cost == 9000


class TestCostEstimate:
    def test_compute_totals(self):
        est = CostEstimate(square_footage=2500)
        est.line_items = [
            LineItem(description="Mat", csi_division=CSIDivision.DIV_06_WOOD,
                     quantity=10, unit=UnitType.EA, unit_cost=100,
                     total_cost=1000, category="material"),
            LineItem(description="Lab", csi_division=CSIDivision.DIV_06_WOOD,
                     quantity=20, unit=UnitType.HR, unit_cost=50,
                     total_cost=1000, category="labor"),
        ]
        est.compute_totals()
        assert est.subtotal_material == 1000
        assert est.subtotal_labor == 1000
        assert est.subtotal == 2000
        assert est.cost_per_sqft == pytest.approx(0.8)

    def test_empty_estimate(self):
        est = CostEstimate(square_footage=1000)
        est.compute_totals()
        assert est.total_cost == 0


class TestEnums:
    def test_all_csi_divisions(self):
        assert len(CSIDivision) == 16

    def test_project_types(self):
        assert len(ProjectType) == 5

    def test_regions(self):
        assert len(Region) == 6

    def test_unit_types(self):
        assert len(UnitType) >= 10
