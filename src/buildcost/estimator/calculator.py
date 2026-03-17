"""Cost calculator computing material, labor, and equipment costs per trade.

The calculator uses square footage, project type, number of stories, and region
to generate a comprehensive cost estimate organized by CSI divisions.
"""

from __future__ import annotations

import numpy as np

from buildcost.models import (
    ContingencyItem,
    CostEstimate,
    CSIDivision,
    DivisionCost,
    LineItem,
    ProjectType,
    Region,
    UnitType,
)
from buildcost.estimator.materials import MaterialDatabase
from buildcost.estimator.labor import LaborRateDatabase
from buildcost.analyzer.contingency import ContingencyCalculator


class CostCalculator:
    """Computes construction cost estimates based on project parameters.

    Uses material database, labor rates, and industry-standard ratios to
    generate detailed cost breakdowns by CSI division.
    """

    # Approximate material quantity factors per square foot by project type
    # These are industry-standard multipliers for estimating
    QUANTITY_FACTORS: dict[ProjectType, dict[str, float]] = {
        ProjectType.RESIDENTIAL: {
            "concrete_cy_per_sqft": 0.03,
            "rebar_lf_per_sqft": 0.5,
            "lumber_bf_per_sqft": 12.0,
            "sheathing_sqft_per_sqft": 1.5,
            "insulation_sqft_per_sqft": 2.0,
            "drywall_sqft_per_sqft": 3.2,
            "roofing_sq_per_sqft": 0.013,
            "paint_gal_per_sqft": 0.02,
            "flooring_sqft_per_sqft": 1.0,
            "electrical_outlets_per_sqft": 0.04,
            "lighting_per_sqft": 0.02,
            "wire_lf_per_sqft": 1.5,
            "plumbing_lf_per_sqft": 0.5,
            "hvac_lf_per_sqft": 0.3,
            "windows_per_sqft": 0.006,
            "int_doors_per_sqft": 0.004,
        },
        ProjectType.COMMERCIAL: {
            "concrete_cy_per_sqft": 0.05,
            "rebar_lf_per_sqft": 1.0,
            "lumber_bf_per_sqft": 4.0,
            "sheathing_sqft_per_sqft": 0.5,
            "insulation_sqft_per_sqft": 1.8,
            "drywall_sqft_per_sqft": 3.5,
            "roofing_sq_per_sqft": 0.012,
            "paint_gal_per_sqft": 0.018,
            "flooring_sqft_per_sqft": 1.0,
            "electrical_outlets_per_sqft": 0.06,
            "lighting_per_sqft": 0.03,
            "wire_lf_per_sqft": 2.0,
            "plumbing_lf_per_sqft": 0.3,
            "hvac_lf_per_sqft": 0.5,
            "windows_per_sqft": 0.008,
            "int_doors_per_sqft": 0.003,
        },
        ProjectType.INDUSTRIAL: {
            "concrete_cy_per_sqft": 0.06,
            "rebar_lf_per_sqft": 1.2,
            "lumber_bf_per_sqft": 2.0,
            "sheathing_sqft_per_sqft": 0.3,
            "insulation_sqft_per_sqft": 1.5,
            "drywall_sqft_per_sqft": 1.0,
            "roofing_sq_per_sqft": 0.011,
            "paint_gal_per_sqft": 0.01,
            "flooring_sqft_per_sqft": 0.5,
            "electrical_outlets_per_sqft": 0.03,
            "lighting_per_sqft": 0.015,
            "wire_lf_per_sqft": 2.5,
            "plumbing_lf_per_sqft": 0.2,
            "hvac_lf_per_sqft": 0.4,
            "windows_per_sqft": 0.003,
            "int_doors_per_sqft": 0.002,
        },
        ProjectType.INSTITUTIONAL: {
            "concrete_cy_per_sqft": 0.04,
            "rebar_lf_per_sqft": 0.8,
            "lumber_bf_per_sqft": 6.0,
            "sheathing_sqft_per_sqft": 1.0,
            "insulation_sqft_per_sqft": 2.2,
            "drywall_sqft_per_sqft": 3.8,
            "roofing_sq_per_sqft": 0.012,
            "paint_gal_per_sqft": 0.022,
            "flooring_sqft_per_sqft": 1.0,
            "electrical_outlets_per_sqft": 0.05,
            "lighting_per_sqft": 0.035,
            "wire_lf_per_sqft": 2.0,
            "plumbing_lf_per_sqft": 0.4,
            "hvac_lf_per_sqft": 0.5,
            "windows_per_sqft": 0.007,
            "int_doors_per_sqft": 0.005,
        },
        ProjectType.RENOVATION: {
            "concrete_cy_per_sqft": 0.01,
            "rebar_lf_per_sqft": 0.2,
            "lumber_bf_per_sqft": 5.0,
            "sheathing_sqft_per_sqft": 0.5,
            "insulation_sqft_per_sqft": 1.0,
            "drywall_sqft_per_sqft": 2.5,
            "roofing_sq_per_sqft": 0.008,
            "paint_gal_per_sqft": 0.025,
            "flooring_sqft_per_sqft": 0.8,
            "electrical_outlets_per_sqft": 0.03,
            "lighting_per_sqft": 0.015,
            "wire_lf_per_sqft": 1.0,
            "plumbing_lf_per_sqft": 0.3,
            "hvac_lf_per_sqft": 0.2,
            "windows_per_sqft": 0.004,
            "int_doors_per_sqft": 0.003,
        },
    }

    # Labor hours per square foot by trade (residential baseline)
    LABOR_HOURS_PER_SQFT: dict[str, float] = {
        "general_laborer": 0.5,
        "carpenter": 1.2,
        "concrete_finisher": 0.15,
        "electrician": 0.4,
        "plumber": 0.3,
        "hvac_technician": 0.2,
        "roofer": 0.1,
        "drywall_installer": 0.3,
        "painter": 0.25,
        "tile_setter": 0.08,
        "flooring_installer": 0.1,
        "insulation_installer": 0.08,
    }

    # Equipment daily rates
    EQUIPMENT_RATES: dict[str, dict] = {
        "excavator": {"daily_rate": 650.0, "days_per_1000sqft": 1.5},
        "backhoe": {"daily_rate": 450.0, "days_per_1000sqft": 1.0},
        "concrete_pump": {"daily_rate": 1200.0, "days_per_1000sqft": 0.3},
        "crane_mobile": {"daily_rate": 1800.0, "days_per_1000sqft": 0.2},
        "scaffolding": {"daily_rate": 150.0, "days_per_1000sqft": 5.0},
        "dumpster": {"daily_rate": 50.0, "days_per_1000sqft": 10.0},
        "generator": {"daily_rate": 125.0, "days_per_1000sqft": 3.0},
        "compactor": {"daily_rate": 200.0, "days_per_1000sqft": 0.5},
    }

    def __init__(self):
        self.material_db = MaterialDatabase()
        self._contingency_calc = ContingencyCalculator()

    def estimate(
        self,
        square_footage: float,
        project_type: str | ProjectType = "residential",
        stories: int = 1,
        region: str | Region = "southeast",
        project_name: str = "Construction Project",
        include_contingency: bool = True,
    ) -> CostEstimate:
        """Generate a complete cost estimate.

        Args:
            square_footage: Total building area in square feet.
            project_type: Type of construction project.
            stories: Number of stories.
            region: Geographic region for labor cost adjustment.
            project_name: Name for the estimate.
            include_contingency: Whether to add contingency amounts.

        Returns:
            Complete CostEstimate with line items, division costs, and totals.
        """
        if isinstance(project_type, str):
            project_type = ProjectType(project_type.lower())
        if isinstance(region, str):
            region = Region(region.lower())

        labor_db = LaborRateDatabase(region)
        factors = self.QUANTITY_FACTORS.get(project_type, self.QUANTITY_FACTORS[ProjectType.RESIDENTIAL])

        # Story multiplier: each additional story adds complexity
        story_multiplier = 1.0 + (stories - 1) * 0.15

        line_items: list[LineItem] = []

        # ── Generate material line items ──
        line_items.extend(self._calc_site_materials(square_footage, factors))
        line_items.extend(self._calc_concrete_materials(square_footage, factors))
        line_items.extend(self._calc_wood_materials(square_footage, factors))
        line_items.extend(self._calc_thermal_materials(square_footage, factors))
        line_items.extend(self._calc_openings_materials(square_footage, factors))
        line_items.extend(self._calc_finishes_materials(square_footage, factors))
        line_items.extend(self._calc_mechanical_materials(square_footage, factors))
        line_items.extend(self._calc_electrical_materials(square_footage, factors))

        # ── Generate labor line items ──
        for trade, hrs_per_sqft in self.LABOR_HOURS_PER_SQFT.items():
            hours = square_footage * hrs_per_sqft * story_multiplier
            rate = labor_db.get_rate(trade)
            info = labor_db.get_rate_info(trade)

            # Map trade to CSI division
            div_map = {
                "general_laborer": CSIDivision.DIV_01_GENERAL,
                "carpenter": CSIDivision.DIV_06_WOOD,
                "concrete_finisher": CSIDivision.DIV_03_CONCRETE,
                "electrician": CSIDivision.DIV_16_ELECTRICAL,
                "plumber": CSIDivision.DIV_15_MECHANICAL,
                "hvac_technician": CSIDivision.DIV_15_MECHANICAL,
                "roofer": CSIDivision.DIV_07_THERMAL,
                "drywall_installer": CSIDivision.DIV_09_FINISHES,
                "painter": CSIDivision.DIV_09_FINISHES,
                "tile_setter": CSIDivision.DIV_09_FINISHES,
                "flooring_installer": CSIDivision.DIV_09_FINISHES,
                "insulation_installer": CSIDivision.DIV_07_THERMAL,
            }

            line_items.append(LineItem(
                description=f"Labor: {info['title']}",
                csi_division=div_map.get(trade, CSIDivision.DIV_01_GENERAL),
                quantity=round(hours, 1),
                unit=UnitType.HR,
                unit_cost=rate,
                total_cost=round(hours * rate, 2),
                category="labor",
            ))

        # ── Generate equipment line items ──
        for equip, rates in self.EQUIPMENT_RATES.items():
            days = (square_footage / 1000) * rates["days_per_1000sqft"] * story_multiplier
            if days < 0.5:
                days = 0.5  # minimum half day
            total = days * rates["daily_rate"]

            line_items.append(LineItem(
                description=f"Equipment: {equip.replace('_', ' ').title()}",
                csi_division=CSIDivision.DIV_01_GENERAL,
                quantity=round(days, 1),
                unit=UnitType.EA,
                unit_cost=rates["daily_rate"],
                total_cost=round(total, 2),
                category="equipment",
            ))

        # ── Build estimate ──
        estimate = CostEstimate(
            project_name=project_name,
            project_type=project_type,
            region=region,
            square_footage=square_footage,
            stories=stories,
            line_items=line_items,
        )

        # Build division cost summaries
        estimate.division_costs = self._build_division_costs(line_items)

        # Compute subtotals
        estimate.compute_totals()

        # Add contingencies
        if include_contingency:
            contingencies = self._contingency_calc.calculate(
                estimate.subtotal, project_type, stories,
            )
            estimate.contingencies = contingencies
            estimate.compute_totals()

        return estimate

    def _calc_site_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Gravel base for foundation
        gravel_cy = sqft * 0.008
        items.append(LineItem(
            description="Gravel Base (3/4 inch)", csi_division=CSIDivision.DIV_02_SITE,
            quantity=round(gravel_cy, 1), unit=UnitType.CY, unit_cost=28.00,
            total_cost=round(gravel_cy * 28.00, 2), category="material",
        ))
        # Geotextile fabric
        fabric_sqft = sqft * 0.5
        items.append(LineItem(
            description="Geotextile Fabric", csi_division=CSIDivision.DIV_02_SITE,
            quantity=round(fabric_sqft, 1), unit=UnitType.SQFT, unit_cost=0.45,
            total_cost=round(fabric_sqft * 0.45, 2), category="material",
        ))
        return items

    def _calc_concrete_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        conc_cy = sqft * factors["concrete_cy_per_sqft"]
        items.append(LineItem(
            description="Ready-Mix Concrete 3000 PSI", csi_division=CSIDivision.DIV_03_CONCRETE,
            quantity=round(conc_cy, 1), unit=UnitType.CY, unit_cost=145.00,
            total_cost=round(conc_cy * 145.00, 2), category="material",
        ))
        rebar_lf = sqft * factors["rebar_lf_per_sqft"]
        items.append(LineItem(
            description="Rebar #4 (1/2 inch)", csi_division=CSIDivision.DIV_03_CONCRETE,
            quantity=round(rebar_lf, 1), unit=UnitType.LF, unit_cost=1.10,
            total_cost=round(rebar_lf * 1.10, 2), category="material",
        ))
        mesh_sqft = sqft * 0.5
        items.append(LineItem(
            description="Wire Mesh 6x6 W1.4", csi_division=CSIDivision.DIV_03_CONCRETE,
            quantity=round(mesh_sqft, 1), unit=UnitType.SQFT, unit_cost=0.35,
            total_cost=round(mesh_sqft * 0.35, 2), category="material",
        ))
        return items

    def _calc_wood_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Framing lumber (converted from board feet to stud count approximation)
        studs = sqft * factors["lumber_bf_per_sqft"] / 5.33  # ~5.33 bf per 2x4x8
        items.append(LineItem(
            description="SPF Lumber 2x4x8 (Framing)", csi_division=CSIDivision.DIV_06_WOOD,
            quantity=round(studs, 0), unit=UnitType.EA, unit_cost=4.25,
            total_cost=round(studs * 4.25, 2), category="material",
        ))
        # Sheathing
        sheets = sqft * factors["sheathing_sqft_per_sqft"] / 32  # 32 sqft per sheet
        items.append(LineItem(
            description="OSB Sheathing 7/16 inch", csi_division=CSIDivision.DIV_06_WOOD,
            quantity=round(sheets, 0), unit=UnitType.SHEET, unit_cost=22.00,
            total_cost=round(sheets * 22.00, 2), category="material",
        ))
        # Subfloor
        subfloor = sqft / 32  # one layer of subfloor
        items.append(LineItem(
            description="Plywood Sheathing 3/4 inch T&G (Subfloor)", csi_division=CSIDivision.DIV_06_WOOD,
            quantity=round(subfloor, 0), unit=UnitType.SHEET, unit_cost=48.00,
            total_cost=round(subfloor * 48.00, 2), category="material",
        ))
        return items

    def _calc_thermal_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Wall insulation
        insul = sqft * factors["insulation_sqft_per_sqft"] * 0.5
        items.append(LineItem(
            description="Fiberglass Batt R-13 (Walls)", csi_division=CSIDivision.DIV_07_THERMAL,
            quantity=round(insul, 0), unit=UnitType.SQFT, unit_cost=0.55,
            total_cost=round(insul * 0.55, 2), category="material",
        ))
        # Attic insulation
        attic = sqft * 1.0
        items.append(LineItem(
            description="Fiberglass Batt R-30 (Attic)", csi_division=CSIDivision.DIV_07_THERMAL,
            quantity=round(attic, 0), unit=UnitType.SQFT, unit_cost=1.10,
            total_cost=round(attic * 1.10, 2), category="material",
        ))
        # Roofing
        roof_sq = sqft * factors["roofing_sq_per_sqft"]
        items.append(LineItem(
            description="Asphalt Shingles (30-year)", csi_division=CSIDivision.DIV_07_THERMAL,
            quantity=round(roof_sq, 1), unit=UnitType.SQ, unit_cost=110.00,
            total_cost=round(roof_sq * 110.00, 2), category="material",
        ))
        # House wrap
        wrap_rolls = sqft * factors["sheathing_sqft_per_sqft"] / 1350  # ~1350 sqft per roll
        items.append(LineItem(
            description="House Wrap", csi_division=CSIDivision.DIV_07_THERMAL,
            quantity=max(1, round(wrap_rolls, 0)), unit=UnitType.ROLL, unit_cost=165.00,
            total_cost=round(max(1, wrap_rolls) * 165.00, 2), category="material",
        ))
        return items

    def _calc_openings_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Windows
        windows = max(4, round(sqft * factors["windows_per_sqft"]))
        items.append(LineItem(
            description="Vinyl Window Double Hung 3x4", csi_division=CSIDivision.DIV_08_OPENINGS,
            quantity=windows, unit=UnitType.EA, unit_cost=285.00,
            total_cost=round(windows * 285.00, 2), category="material",
        ))
        # Exterior doors
        ext_doors = max(2, round(sqft * 0.001))
        items.append(LineItem(
            description="Exterior Door (Steel Insulated)", csi_division=CSIDivision.DIV_08_OPENINGS,
            quantity=ext_doors, unit=UnitType.EA, unit_cost=350.00,
            total_cost=round(ext_doors * 350.00, 2), category="material",
        ))
        # Interior doors
        int_doors = max(5, round(sqft * factors["int_doors_per_sqft"]))
        items.append(LineItem(
            description="Interior Door (Hollow Core)", csi_division=CSIDivision.DIV_08_OPENINGS,
            quantity=int_doors, unit=UnitType.EA, unit_cost=85.00,
            total_cost=round(int_doors * 85.00, 2), category="material",
        ))
        return items

    def _calc_finishes_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Drywall
        dw_sheets = sqft * factors["drywall_sqft_per_sqft"] / 32
        items.append(LineItem(
            description="Drywall 1/2 inch Regular", csi_division=CSIDivision.DIV_09_FINISHES,
            quantity=round(dw_sheets, 0), unit=UnitType.SHEET, unit_cost=14.50,
            total_cost=round(dw_sheets * 14.50, 2), category="material",
        ))
        # Joint compound
        jc_gal = dw_sheets * 0.5
        items.append(LineItem(
            description="Joint Compound (All Purpose)", csi_division=CSIDivision.DIV_09_FINISHES,
            quantity=round(jc_gal, 1), unit=UnitType.GAL, unit_cost=12.00,
            total_cost=round(jc_gal * 12.00, 2), category="material",
        ))
        # Paint
        paint_gal = sqft * factors["paint_gal_per_sqft"]
        items.append(LineItem(
            description="Interior Paint (Premium)", csi_division=CSIDivision.DIV_09_FINISHES,
            quantity=round(paint_gal, 1), unit=UnitType.GAL, unit_cost=45.00,
            total_cost=round(paint_gal * 45.00, 2), category="material",
        ))
        # Flooring (mix of LVP and carpet)
        lvp_sqft = sqft * factors["flooring_sqft_per_sqft"] * 0.6
        carpet_sqft = sqft * factors["flooring_sqft_per_sqft"] * 0.4
        items.append(LineItem(
            description="Luxury Vinyl Plank", csi_division=CSIDivision.DIV_09_FINISHES,
            quantity=round(lvp_sqft, 0), unit=UnitType.SQFT, unit_cost=3.25,
            total_cost=round(lvp_sqft * 3.25, 2), category="material",
        ))
        items.append(LineItem(
            description="Carpet (Mid-Grade)", csi_division=CSIDivision.DIV_09_FINISHES,
            quantity=round(carpet_sqft, 0), unit=UnitType.SQFT, unit_cost=3.50,
            total_cost=round(carpet_sqft * 3.50, 2), category="material",
        ))
        return items

    def _calc_mechanical_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # HVAC system
        tons = max(1.5, sqft / 600)  # ~600 sqft per ton rule of thumb
        hvac_count = max(1, round(tons / 3))  # 3-ton units
        items.append(LineItem(
            description="HVAC Split System 3 Ton", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=hvac_count, unit=UnitType.EA, unit_cost=4500.00,
            total_cost=round(hvac_count * 4500.00, 2), category="material",
        ))
        # Ductwork
        duct_lf = sqft * factors["hvac_lf_per_sqft"]
        items.append(LineItem(
            description="HVAC Ductwork (Sheet Metal)", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=round(duct_lf, 0), unit=UnitType.LF, unit_cost=18.00,
            total_cost=round(duct_lf * 18.00, 2), category="material",
        ))
        # Plumbing supply
        plumb_lf = sqft * factors["plumbing_lf_per_sqft"]
        items.append(LineItem(
            description="PEX Tubing 3/4 inch", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=round(plumb_lf, 0), unit=UnitType.LF, unit_cost=1.25,
            total_cost=round(plumb_lf * 1.25, 2), category="material",
        ))
        # Water heater
        items.append(LineItem(
            description="Water Heater 50 Gal Gas", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=1, unit=UnitType.EA, unit_cost=850.00,
            total_cost=850.00, category="material",
        ))
        # Fixtures
        bathrooms = max(1, round(sqft / 600))
        items.append(LineItem(
            description="Toilet (Standard)", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=bathrooms, unit=UnitType.EA, unit_cost=250.00,
            total_cost=round(bathrooms * 250.00, 2), category="material",
        ))
        items.append(LineItem(
            description="Bathroom Vanity 36 inch", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=bathrooms, unit=UnitType.EA, unit_cost=450.00,
            total_cost=round(bathrooms * 450.00, 2), category="material",
        ))
        items.append(LineItem(
            description="Kitchen Sink (Stainless)", csi_division=CSIDivision.DIV_15_MECHANICAL,
            quantity=1, unit=UnitType.EA, unit_cost=275.00,
            total_cost=275.00, category="material",
        ))
        return items

    def _calc_electrical_materials(self, sqft: float, factors: dict) -> list[LineItem]:
        items = []
        # Panel
        items.append(LineItem(
            description="Electrical Panel 200 Amp", csi_division=CSIDivision.DIV_16_ELECTRICAL,
            quantity=1, unit=UnitType.EA, unit_cost=350.00,
            total_cost=350.00, category="material",
        ))
        # Wire
        wire_lf = sqft * factors["wire_lf_per_sqft"]
        items.append(LineItem(
            description="Romex 12/2 NM-B", csi_division=CSIDivision.DIV_16_ELECTRICAL,
            quantity=round(wire_lf, 0), unit=UnitType.LF, unit_cost=0.65,
            total_cost=round(wire_lf * 0.65, 2), category="material",
        ))
        # Outlets
        outlets = max(10, round(sqft * factors["electrical_outlets_per_sqft"]))
        items.append(LineItem(
            description="Duplex Receptacle 15A", csi_division=CSIDivision.DIV_16_ELECTRICAL,
            quantity=outlets, unit=UnitType.EA, unit_cost=1.50,
            total_cost=round(outlets * 1.50, 2), category="material",
        ))
        # Lights
        lights = max(8, round(sqft * factors["lighting_per_sqft"]))
        items.append(LineItem(
            description="LED Recessed Light 6 inch", csi_division=CSIDivision.DIV_16_ELECTRICAL,
            quantity=lights, unit=UnitType.EA, unit_cost=22.00,
            total_cost=round(lights * 22.00, 2), category="material",
        ))
        # Smoke detectors
        smokes = max(3, round(sqft / 500))
        items.append(LineItem(
            description="Smoke Detector (Hardwired)", csi_division=CSIDivision.DIV_16_ELECTRICAL,
            quantity=smokes, unit=UnitType.EA, unit_cost=28.00,
            total_cost=round(smokes * 28.00, 2), category="material",
        ))
        return items

    def _build_division_costs(self, line_items: list[LineItem]) -> list[DivisionCost]:
        """Aggregate line items into division costs."""
        div_data: dict[CSIDivision, DivisionCost] = {}
        for li in line_items:
            if li.csi_division not in div_data:
                div_data[li.csi_division] = DivisionCost(
                    division=li.csi_division,
                )
            dc = div_data[li.csi_division]
            dc.line_items.append(li)
            if li.category == "material":
                dc.material_cost += li.total_cost
            elif li.category == "labor":
                dc.labor_cost += li.total_cost
            elif li.category == "equipment":
                dc.equipment_cost += li.total_cost

        return sorted(div_data.values(), key=lambda d: d.division.value)
