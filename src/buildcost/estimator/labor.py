"""Labor rate database with hourly rates by trade and region.

Rates are approximate 2024-2025 US averages including benefits and burden.
Regional multipliers adjust for cost-of-living differences.
"""

from __future__ import annotations

from buildcost.models import Region


# Regional cost multipliers (relative to national average)
REGIONAL_MULTIPLIERS: dict[Region, float] = {
    Region.NORTHEAST: 1.25,
    Region.SOUTHEAST: 0.90,
    Region.MIDWEST: 0.95,
    Region.SOUTHWEST: 1.00,
    Region.WEST: 1.30,
    Region.NORTHWEST: 1.15,
}


class LaborRateDatabase:
    """Database of labor rates by construction trade and region.

    All rates are fully burdened (include benefits, insurance, taxes).
    """

    # Base hourly rates (national average, fully burdened)
    BASE_RATES: dict[str, dict] = {
        "general_laborer": {
            "title": "General Laborer",
            "base_rate": 28.00,
            "description": "General site labor, cleanup, material handling",
        },
        "carpenter": {
            "title": "Carpenter",
            "base_rate": 42.00,
            "description": "Rough and finish carpentry, framing, trim",
        },
        "carpenter_foreman": {
            "title": "Carpenter Foreman",
            "base_rate": 52.00,
            "description": "Lead carpenter overseeing crew",
        },
        "concrete_finisher": {
            "title": "Concrete Finisher",
            "base_rate": 40.00,
            "description": "Concrete placement, finishing, flatwork",
        },
        "mason": {
            "title": "Mason/Bricklayer",
            "base_rate": 48.00,
            "description": "Brick, block, stone masonry",
        },
        "ironworker": {
            "title": "Ironworker",
            "base_rate": 55.00,
            "description": "Structural steel erection and reinforcing",
        },
        "electrician": {
            "title": "Electrician",
            "base_rate": 55.00,
            "description": "Electrical wiring, panels, fixtures",
        },
        "electrician_apprentice": {
            "title": "Electrician Apprentice",
            "base_rate": 32.00,
            "description": "Electrical helper and trainee",
        },
        "plumber": {
            "title": "Plumber",
            "base_rate": 58.00,
            "description": "Plumbing rough-in and finish",
        },
        "plumber_apprentice": {
            "title": "Plumber Apprentice",
            "base_rate": 34.00,
            "description": "Plumbing helper and trainee",
        },
        "hvac_technician": {
            "title": "HVAC Technician",
            "base_rate": 52.00,
            "description": "HVAC installation, ductwork, equipment",
        },
        "roofer": {
            "title": "Roofer",
            "base_rate": 38.00,
            "description": "Roofing installation and repair",
        },
        "drywall_installer": {
            "title": "Drywall Installer",
            "base_rate": 36.00,
            "description": "Drywall hanging, taping, finishing",
        },
        "painter": {
            "title": "Painter",
            "base_rate": 35.00,
            "description": "Interior and exterior painting",
        },
        "tile_setter": {
            "title": "Tile Setter",
            "base_rate": 45.00,
            "description": "Ceramic, porcelain, stone tile installation",
        },
        "flooring_installer": {
            "title": "Flooring Installer",
            "base_rate": 38.00,
            "description": "Hardwood, LVP, carpet installation",
        },
        "insulation_installer": {
            "title": "Insulation Installer",
            "base_rate": 32.00,
            "description": "Batt, blown, spray foam insulation",
        },
        "siding_installer": {
            "title": "Siding Installer",
            "base_rate": 40.00,
            "description": "Vinyl, fiber cement, wood siding",
        },
        "excavation_operator": {
            "title": "Excavation Equipment Operator",
            "base_rate": 50.00,
            "description": "Backhoe, excavator, dozer operation",
        },
        "crane_operator": {
            "title": "Crane Operator",
            "base_rate": 62.00,
            "description": "Mobile and tower crane operation",
        },
        "welder": {
            "title": "Welder/Fitter",
            "base_rate": 50.00,
            "description": "Structural and pipe welding",
        },
        "glazier": {
            "title": "Glazier",
            "base_rate": 45.00,
            "description": "Glass and window installation",
        },
        "sheet_metal_worker": {
            "title": "Sheet Metal Worker",
            "base_rate": 50.00,
            "description": "HVAC ductwork, flashing, metal work",
        },
        "concrete_pump_operator": {
            "title": "Concrete Pump Operator",
            "base_rate": 48.00,
            "description": "Concrete pump truck operation",
        },
        "superintendent": {
            "title": "Project Superintendent",
            "base_rate": 72.00,
            "description": "On-site project management and coordination",
        },
    }

    def __init__(self, region: Region = Region.SOUTHEAST):
        self.region = region
        self._multiplier = REGIONAL_MULTIPLIERS.get(region, 1.0)

    def get_rate(self, trade: str) -> float:
        """Get the regional hourly rate for a trade.

        Args:
            trade: Trade key (e.g., 'carpenter', 'electrician').

        Returns:
            Hourly rate adjusted for region.
        """
        trade_info = self.BASE_RATES.get(trade)
        if trade_info is None:
            raise ValueError(f"Unknown trade: '{trade}'. Available: {list(self.BASE_RATES.keys())}")
        return round(trade_info["base_rate"] * self._multiplier, 2)

    def get_rate_info(self, trade: str) -> dict:
        """Get full rate info including title, base rate, and regional rate."""
        trade_info = self.BASE_RATES.get(trade)
        if trade_info is None:
            raise ValueError(f"Unknown trade: '{trade}'")
        return {
            "trade": trade,
            "title": trade_info["title"],
            "base_rate": trade_info["base_rate"],
            "regional_rate": round(trade_info["base_rate"] * self._multiplier, 2),
            "region": self.region.value,
            "multiplier": self._multiplier,
            "description": trade_info["description"],
        }

    def get_all_rates(self) -> dict[str, float]:
        """Get all regional rates."""
        return {trade: self.get_rate(trade) for trade in self.BASE_RATES}

    def list_trades(self) -> list[str]:
        """Get all available trade keys."""
        return list(self.BASE_RATES.keys())

    def search_trades(self, query: str) -> list[dict]:
        """Search trades by name or description."""
        q = query.lower()
        results = []
        for trade, info in self.BASE_RATES.items():
            if q in trade.lower() or q in info["title"].lower() or q in info["description"].lower():
                results.append(self.get_rate_info(trade))
        return results

    @classmethod
    def get_regional_multiplier(cls, region: Region) -> float:
        return REGIONAL_MULTIPLIERS.get(region, 1.0)

    @classmethod
    def compare_regions(cls, trade: str) -> dict[str, float]:
        """Compare a trade's rate across all regions."""
        base = cls.BASE_RATES.get(trade)
        if base is None:
            raise ValueError(f"Unknown trade: '{trade}'")
        return {
            region.value: round(base["base_rate"] * mult, 2)
            for region, mult in REGIONAL_MULTIPLIERS.items()
        }
