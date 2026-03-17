"""Pydantic models for construction cost estimation."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Types of construction projects."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    INSTITUTIONAL = "institutional"
    RENOVATION = "renovation"


class Region(str, Enum):
    """Geographic regions affecting costs."""

    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    MIDWEST = "midwest"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"


class CSIDivision(str, Enum):
    """CSI MasterFormat Divisions."""

    DIV_01_GENERAL = "01 - General Requirements"
    DIV_02_SITE = "02 - Site Construction"
    DIV_03_CONCRETE = "03 - Concrete"
    DIV_04_MASONRY = "04 - Masonry"
    DIV_05_METALS = "05 - Metals"
    DIV_06_WOOD = "06 - Wood, Plastics & Composites"
    DIV_07_THERMAL = "07 - Thermal & Moisture Protection"
    DIV_08_OPENINGS = "08 - Openings (Doors & Windows)"
    DIV_09_FINISHES = "09 - Finishes"
    DIV_10_SPECIALTIES = "10 - Specialties"
    DIV_11_EQUIPMENT = "11 - Equipment"
    DIV_12_FURNISHINGS = "12 - Furnishings"
    DIV_13_SPECIAL = "13 - Special Construction"
    DIV_14_CONVEYING = "14 - Conveying Equipment"
    DIV_15_MECHANICAL = "15 - Mechanical (HVAC)"
    DIV_16_ELECTRICAL = "16 - Electrical"


class UnitType(str, Enum):
    """Units of measurement for materials."""

    SQFT = "sqft"
    LF = "lf"          # linear feet
    CY = "cy"          # cubic yards
    EA = "ea"          # each
    TON = "ton"
    GAL = "gal"
    BF = "bf"          # board feet
    SQ = "sq"          # roofing square (100 sqft)
    SF = "sf"          # square feet
    HR = "hr"          # hours
    BAG = "bag"
    ROLL = "roll"
    SHEET = "sheet"
    LB = "lb"


class Material(BaseModel):
    """A construction material with cost information."""

    name: str
    category: str
    csi_division: CSIDivision
    unit: UnitType
    unit_cost: float = Field(gt=0, description="Cost per unit in USD")
    description: str = ""
    waste_factor: float = Field(default=0.05, ge=0, le=0.5, description="Waste percentage 0-50%")


class LineItem(BaseModel):
    """A single line item in a cost estimate."""

    description: str
    csi_division: CSIDivision
    quantity: float = Field(ge=0)
    unit: UnitType
    unit_cost: float = Field(ge=0)
    total_cost: float = Field(ge=0)
    category: str = Field(default="material", description="material, labor, or equipment")
    notes: str = ""

    @property
    def computed_total(self) -> float:
        return self.quantity * self.unit_cost


class DivisionCost(BaseModel):
    """Aggregated cost for a CSI division."""

    division: CSIDivision
    material_cost: float = 0.0
    labor_cost: float = 0.0
    equipment_cost: float = 0.0
    line_items: list[LineItem] = Field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return self.material_cost + self.labor_cost + self.equipment_cost

    @property
    def percentage_of_total(self) -> float:
        """Placeholder - set by parent estimate."""
        return 0.0


class ContingencyItem(BaseModel):
    """A contingency line item."""

    name: str
    percentage: float = Field(ge=0, le=100)
    amount: float = Field(ge=0)
    reason: str = ""


class CostEstimate(BaseModel):
    """Complete cost estimate for a construction project."""

    project_name: str = "Construction Project"
    project_type: ProjectType = ProjectType.RESIDENTIAL
    region: Region = Region.SOUTHEAST
    square_footage: float = Field(gt=0)
    stories: int = Field(default=1, ge=1, le=100)

    division_costs: list[DivisionCost] = Field(default_factory=list)
    line_items: list[LineItem] = Field(default_factory=list)
    contingencies: list[ContingencyItem] = Field(default_factory=list)

    subtotal_material: float = 0.0
    subtotal_labor: float = 0.0
    subtotal_equipment: float = 0.0
    subtotal: float = 0.0
    contingency_total: float = 0.0
    total_cost: float = 0.0
    cost_per_sqft: float = 0.0

    def compute_totals(self) -> None:
        """Recompute all totals from line items."""
        self.subtotal_material = sum(
            li.total_cost for li in self.line_items if li.category == "material"
        )
        self.subtotal_labor = sum(
            li.total_cost for li in self.line_items if li.category == "labor"
        )
        self.subtotal_equipment = sum(
            li.total_cost for li in self.line_items if li.category == "equipment"
        )
        self.subtotal = self.subtotal_material + self.subtotal_labor + self.subtotal_equipment
        self.contingency_total = sum(c.amount for c in self.contingencies)
        self.total_cost = self.subtotal + self.contingency_total
        self.cost_per_sqft = self.total_cost / self.square_footage if self.square_footage else 0

    def get_division_summary(self) -> dict[str, float]:
        """Get cost summary by CSI division."""
        summary: dict[str, float] = {}
        for dc in self.division_costs:
            summary[dc.division.value] = dc.total_cost
        return summary


class Project(BaseModel):
    """A construction project with metadata."""

    name: str
    project_type: ProjectType
    region: Region
    square_footage: float = Field(gt=0)
    stories: int = Field(default=1, ge=1)
    description: str = ""
    estimate: Optional[CostEstimate] = None
