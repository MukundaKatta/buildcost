"""Material database with 100+ construction materials and unit costs.

Costs are approximate 2024-2025 US averages and vary by region, supplier,
and market conditions. Includes waste factors for each material.
"""

from __future__ import annotations

from buildcost.models import CSIDivision, Material, UnitType


class MaterialDatabase:
    """Database of 100+ construction materials with unit costs."""

    def __init__(self):
        self._materials: list[Material] = self._build_database()
        self._by_name: dict[str, Material] = {m.name.lower(): m for m in self._materials}
        self._by_division: dict[CSIDivision, list[Material]] = {}
        for m in self._materials:
            self._by_division.setdefault(m.csi_division, []).append(m)

    @property
    def materials(self) -> list[Material]:
        return self._materials

    def search(self, query: str) -> list[Material]:
        """Search materials by name or category (case-insensitive)."""
        q = query.lower()
        return [m for m in self._materials if q in m.name.lower() or q in m.category.lower()]

    def get_by_name(self, name: str) -> Material | None:
        return self._by_name.get(name.lower())

    def get_by_division(self, division: CSIDivision) -> list[Material]:
        return self._by_division.get(division, [])

    def get_by_category(self, category: str) -> list[Material]:
        cat = category.lower()
        return [m for m in self._materials if m.category.lower() == cat]

    def _build_database(self) -> list[Material]:
        """Build the complete material database."""
        materials = []

        # ── Division 02: Site Construction ──
        materials.extend([
            Material(name="Topsoil", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.CY, unit_cost=35.00, waste_factor=0.10, description="Screened topsoil for grading"),
            Material(name="Gravel Base (3/4 inch)", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.CY, unit_cost=28.00, waste_factor=0.05, description="Crushed gravel for base courses"),
            Material(name="Sand Fill", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.CY, unit_cost=22.00, waste_factor=0.08, description="Clean fill sand"),
            Material(name="Geotextile Fabric", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.SQFT, unit_cost=0.45, waste_factor=0.10, description="Non-woven separation fabric"),
            Material(name="Erosion Control Blanket", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.SQFT, unit_cost=0.65, waste_factor=0.15, description="Biodegradable erosion mat"),
            Material(name="Silt Fence", category="earthwork", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.LF, unit_cost=3.50, waste_factor=0.05, description="Sediment control fence"),
            Material(name="PVC Drain Pipe 4 inch", category="drainage", csi_division=CSIDivision.DIV_02_SITE, unit=UnitType.LF, unit_cost=4.25, waste_factor=0.05, description="Perforated drain pipe"),
        ])

        # ── Division 03: Concrete ──
        materials.extend([
            Material(name="Ready-Mix Concrete 3000 PSI", category="concrete", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.CY, unit_cost=145.00, waste_factor=0.05, description="Standard structural concrete"),
            Material(name="Ready-Mix Concrete 4000 PSI", category="concrete", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.CY, unit_cost=160.00, waste_factor=0.05, description="High-strength concrete"),
            Material(name="Ready-Mix Concrete 5000 PSI", category="concrete", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.CY, unit_cost=180.00, waste_factor=0.05, description="Extra high-strength concrete"),
            Material(name="Rebar #4 (1/2 inch)", category="reinforcing", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.LF, unit_cost=1.10, waste_factor=0.05, description="Grade 60 reinforcing bar"),
            Material(name="Rebar #5 (5/8 inch)", category="reinforcing", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.LF, unit_cost=1.55, waste_factor=0.05, description="Grade 60 reinforcing bar"),
            Material(name="Wire Mesh 6x6 W1.4", category="reinforcing", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.SQFT, unit_cost=0.35, waste_factor=0.10, description="Welded wire reinforcement"),
            Material(name="Concrete Form Plywood", category="formwork", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.SHEET, unit_cost=45.00, waste_factor=0.15, description="3/4 inch form-grade plywood"),
            Material(name="Form Release Agent", category="formwork", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.GAL, unit_cost=18.00, waste_factor=0.05, description="Concrete form release oil"),
            Material(name="Concrete Sealer", category="concrete", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.GAL, unit_cost=42.00, waste_factor=0.10, description="Penetrating concrete sealer"),
            Material(name="Expansion Joint Filler", category="concrete", csi_division=CSIDivision.DIV_03_CONCRETE, unit=UnitType.LF, unit_cost=2.80, waste_factor=0.05, description="Asphalt-impregnated filler board"),
        ])

        # ── Division 04: Masonry ──
        materials.extend([
            Material(name="CMU Block 8x8x16", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.EA, unit_cost=2.15, waste_factor=0.05, description="Standard concrete masonry unit"),
            Material(name="Face Brick (Standard)", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.EA, unit_cost=0.85, waste_factor=0.05, description="Modular clay face brick"),
            Material(name="Fire Brick", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.EA, unit_cost=3.50, waste_factor=0.05, description="Refractory fire brick"),
            Material(name="Mortar Mix Type S", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.BAG, unit_cost=8.50, waste_factor=0.10, description="80 lb bag structural mortar"),
            Material(name="Mortar Mix Type N", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.BAG, unit_cost=7.50, waste_factor=0.10, description="80 lb bag general purpose mortar"),
            Material(name="Stone Veneer (Natural)", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.SQFT, unit_cost=14.00, waste_factor=0.10, description="Natural thin-cut stone veneer"),
            Material(name="Manufactured Stone Veneer", category="masonry", csi_division=CSIDivision.DIV_04_MASONRY, unit=UnitType.SQFT, unit_cost=9.50, waste_factor=0.10, description="Cultured stone veneer"),
        ])

        # ── Division 05: Metals ──
        materials.extend([
            Material(name="Structural Steel W-Shape", category="structural steel", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.TON, unit_cost=3200.00, waste_factor=0.03, description="Wide flange structural beams"),
            Material(name="Steel Column HSS", category="structural steel", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.TON, unit_cost=3600.00, waste_factor=0.03, description="Hollow structural section columns"),
            Material(name="Steel Joist (Open Web)", category="structural steel", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.LF, unit_cost=18.50, waste_factor=0.03, description="Open web steel joist"),
            Material(name="Metal Deck (1.5 inch)", category="metal deck", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.SQFT, unit_cost=4.25, waste_factor=0.05, description="Galvanized steel roof/floor deck"),
            Material(name="Steel Stud 3-5/8 inch 20ga", category="framing", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.LF, unit_cost=1.45, waste_factor=0.08, description="Light gauge steel framing stud"),
            Material(name="Steel Track 3-5/8 inch", category="framing", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.LF, unit_cost=1.25, waste_factor=0.08, description="Steel stud track/runner"),
            Material(name="Steel Lintels", category="structural steel", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.LF, unit_cost=12.00, waste_factor=0.05, description="Steel angle lintels for openings"),
            Material(name="Anchor Bolts 1/2 inch", category="fasteners", csi_division=CSIDivision.DIV_05_METALS, unit=UnitType.EA, unit_cost=3.75, waste_factor=0.05, description="Galvanized anchor bolts"),
        ])

        # ── Division 06: Wood, Plastics & Composites ──
        materials.extend([
            Material(name="SPF Lumber 2x4x8", category="framing lumber", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.EA, unit_cost=4.25, waste_factor=0.08, description="Spruce-Pine-Fir stud grade"),
            Material(name="SPF Lumber 2x6x8", category="framing lumber", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.EA, unit_cost=6.50, waste_factor=0.08, description="Spruce-Pine-Fir #2 grade"),
            Material(name="SPF Lumber 2x10x12", category="framing lumber", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.EA, unit_cost=14.00, waste_factor=0.08, description="Floor joist lumber"),
            Material(name="SPF Lumber 2x12x12", category="framing lumber", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.EA, unit_cost=18.50, waste_factor=0.08, description="Header and beam lumber"),
            Material(name="Plywood Sheathing 1/2 inch CDX", category="sheathing", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.SHEET, unit_cost=32.00, waste_factor=0.10, description="4x8 wall/roof sheathing"),
            Material(name="Plywood Sheathing 3/4 inch T&G", category="sheathing", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.SHEET, unit_cost=48.00, waste_factor=0.10, description="4x8 subfloor sheathing"),
            Material(name="OSB Sheathing 7/16 inch", category="sheathing", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.SHEET, unit_cost=22.00, waste_factor=0.10, description="Oriented strand board sheathing"),
            Material(name="LVL Beam 1-3/4 x 9-1/2", category="engineered wood", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.LF, unit_cost=8.50, waste_factor=0.05, description="Laminated veneer lumber beam"),
            Material(name="I-Joist 9-1/2 inch", category="engineered wood", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.LF, unit_cost=4.75, waste_factor=0.05, description="Engineered wood I-joist"),
            Material(name="Pressure Treated 4x4x8", category="treated lumber", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.EA, unit_cost=12.50, waste_factor=0.05, description="Ground contact rated post"),
            Material(name="Composite Decking", category="composites", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.LF, unit_cost=4.50, waste_factor=0.10, description="Wood-plastic composite deck board"),
            Material(name="Trim Board PVC 1x4", category="trim", csi_division=CSIDivision.DIV_06_WOOD, unit=UnitType.LF, unit_cost=2.25, waste_factor=0.10, description="Cellular PVC trim board"),
        ])

        # ── Division 07: Thermal & Moisture Protection ──
        materials.extend([
            Material(name="Fiberglass Batt R-13", category="insulation", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQFT, unit_cost=0.55, waste_factor=0.05, description="3-1/2 inch wall insulation"),
            Material(name="Fiberglass Batt R-19", category="insulation", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQFT, unit_cost=0.75, waste_factor=0.05, description="6-1/4 inch wall/floor insulation"),
            Material(name="Fiberglass Batt R-30", category="insulation", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQFT, unit_cost=1.10, waste_factor=0.05, description="10 inch attic insulation"),
            Material(name="Rigid Foam XPS 2 inch", category="insulation", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQFT, unit_cost=1.85, waste_factor=0.08, description="Extruded polystyrene board"),
            Material(name="Spray Foam Closed Cell", category="insulation", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.BF, unit_cost=1.50, waste_factor=0.05, description="Closed cell spray polyurethane"),
            Material(name="Asphalt Shingles (30-year)", category="roofing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQ, unit_cost=110.00, waste_factor=0.10, description="Architectural laminated shingles"),
            Material(name="Asphalt Shingles (50-year)", category="roofing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQ, unit_cost=155.00, waste_factor=0.10, description="Premium architectural shingles"),
            Material(name="Metal Roofing Standing Seam", category="roofing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQ, unit_cost=450.00, waste_factor=0.05, description="26 gauge steel standing seam"),
            Material(name="Ice & Water Shield", category="roofing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.ROLL, unit_cost=85.00, waste_factor=0.10, description="Self-adhering roof underlayment"),
            Material(name="Synthetic Roof Underlayment", category="roofing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.ROLL, unit_cost=65.00, waste_factor=0.10, description="Synthetic felt underlayment"),
            Material(name="House Wrap", category="moisture barrier", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.ROLL, unit_cost=165.00, waste_factor=0.10, description="9x150 ft weather resistive barrier"),
            Material(name="Flashing Aluminum", category="flashing", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.LF, unit_cost=3.50, waste_factor=0.10, description="Step and counter flashing"),
            Material(name="Gutter Aluminum 5 inch", category="drainage", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.LF, unit_cost=6.50, waste_factor=0.05, description="Seamless aluminum gutter"),
            Material(name="Vapor Barrier 6 mil Poly", category="moisture barrier", csi_division=CSIDivision.DIV_07_THERMAL, unit=UnitType.SQFT, unit_cost=0.12, waste_factor=0.10, description="Polyethylene vapor retarder"),
        ])

        # ── Division 08: Openings (Doors & Windows) ──
        materials.extend([
            Material(name="Exterior Door (Steel Insulated)", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=350.00, waste_factor=0.0, description="36 inch pre-hung steel entry door"),
            Material(name="Exterior Door (Fiberglass)", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=550.00, waste_factor=0.0, description="36 inch pre-hung fiberglass entry"),
            Material(name="Interior Door (Hollow Core)", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=85.00, waste_factor=0.0, description="30-36 inch pre-hung interior door"),
            Material(name="Interior Door (Solid Core)", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=175.00, waste_factor=0.0, description="30-36 inch solid core interior"),
            Material(name="Sliding Glass Door 6ft", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=850.00, waste_factor=0.0, description="6 ft vinyl sliding patio door"),
            Material(name="Garage Door 16x7 Insulated", category="doors", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=1200.00, waste_factor=0.0, description="Steel insulated sectional"),
            Material(name="Vinyl Window Double Hung 3x4", category="windows", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=285.00, waste_factor=0.0, description="Double-pane vinyl window"),
            Material(name="Vinyl Window Casement 2x4", category="windows", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=325.00, waste_factor=0.0, description="Casement vinyl window"),
            Material(name="Vinyl Window Picture 4x5", category="windows", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=380.00, waste_factor=0.0, description="Fixed picture window"),
            Material(name="Skylight 2x4 Fixed", category="windows", csi_division=CSIDivision.DIV_08_OPENINGS, unit=UnitType.EA, unit_cost=550.00, waste_factor=0.0, description="Fixed curb-mount skylight"),
        ])

        # ── Division 09: Finishes ──
        materials.extend([
            Material(name="Drywall 1/2 inch Regular", category="drywall", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SHEET, unit_cost=14.50, waste_factor=0.10, description="4x8 standard gypsum board"),
            Material(name="Drywall 5/8 inch Type X", category="drywall", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SHEET, unit_cost=17.50, waste_factor=0.10, description="4x8 fire-rated gypsum board"),
            Material(name="Drywall 1/2 inch Moisture Resistant", category="drywall", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SHEET, unit_cost=18.00, waste_factor=0.10, description="4x8 green board for bathrooms"),
            Material(name="Joint Compound (All Purpose)", category="drywall", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.GAL, unit_cost=12.00, waste_factor=0.10, description="Pre-mixed drywall compound"),
            Material(name="Ceramic Floor Tile 12x12", category="tile", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=3.50, waste_factor=0.10, description="Standard ceramic floor tile"),
            Material(name="Porcelain Tile 12x24", category="tile", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=5.50, waste_factor=0.10, description="Porcelain floor/wall tile"),
            Material(name="Subway Tile 3x6", category="tile", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=4.00, waste_factor=0.10, description="Ceramic subway wall tile"),
            Material(name="Thinset Mortar", category="tile", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.BAG, unit_cost=18.00, waste_factor=0.10, description="50 lb modified thinset"),
            Material(name="Hardwood Flooring Oak 3/4 inch", category="flooring", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=6.50, waste_factor=0.08, description="Solid red oak flooring"),
            Material(name="Luxury Vinyl Plank", category="flooring", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=3.25, waste_factor=0.10, description="Waterproof LVP flooring"),
            Material(name="Carpet (Mid-Grade)", category="flooring", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.SQFT, unit_cost=3.50, waste_factor=0.10, description="Nylon carpet with pad"),
            Material(name="Interior Paint (Premium)", category="paint", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.GAL, unit_cost=45.00, waste_factor=0.10, description="Latex interior paint"),
            Material(name="Exterior Paint (Premium)", category="paint", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.GAL, unit_cost=55.00, waste_factor=0.10, description="Acrylic latex exterior paint"),
            Material(name="Primer (Interior)", category="paint", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.GAL, unit_cost=32.00, waste_factor=0.10, description="Interior latex primer"),
            Material(name="Ceiling Texture Spray", category="finishes", csi_division=CSIDivision.DIV_09_FINISHES, unit=UnitType.GAL, unit_cost=28.00, waste_factor=0.15, description="Spray-on ceiling texture"),
        ])

        # ── Division 10: Specialties ──
        materials.extend([
            Material(name="Bath Accessories Set", category="specialties", csi_division=CSIDivision.DIV_10_SPECIALTIES, unit=UnitType.EA, unit_cost=85.00, waste_factor=0.0, description="Towel bar, TP holder, robe hook"),
            Material(name="Medicine Cabinet", category="specialties", csi_division=CSIDivision.DIV_10_SPECIALTIES, unit=UnitType.EA, unit_cost=120.00, waste_factor=0.0, description="Recessed medicine cabinet with mirror"),
            Material(name="Mailbox (Wall Mount)", category="specialties", csi_division=CSIDivision.DIV_10_SPECIALTIES, unit=UnitType.EA, unit_cost=45.00, waste_factor=0.0, description="Residential wall-mount mailbox"),
            Material(name="Closet Shelving System", category="specialties", csi_division=CSIDivision.DIV_10_SPECIALTIES, unit=UnitType.LF, unit_cost=12.00, waste_factor=0.05, description="Wire shelf and rod system"),
        ])

        # ── Division 15: Mechanical (HVAC) ──
        materials.extend([
            Material(name="HVAC Split System 3 Ton", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=4500.00, waste_factor=0.0, description="Central AC with furnace"),
            Material(name="HVAC Ductwork (Sheet Metal)", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.LF, unit_cost=18.00, waste_factor=0.10, description="Galvanized sheet metal duct"),
            Material(name="HVAC Flex Duct 6 inch", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.LF, unit_cost=4.50, waste_factor=0.10, description="Insulated flexible duct"),
            Material(name="Supply Register 4x10", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=12.00, waste_factor=0.0, description="Steel floor register"),
            Material(name="Return Air Grille 14x20", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=18.00, waste_factor=0.0, description="Steel return air grille"),
            Material(name="Thermostat (Programmable)", category="hvac", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=85.00, waste_factor=0.0, description="Digital programmable thermostat"),
            Material(name="Water Heater 50 Gal Gas", category="plumbing", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=850.00, waste_factor=0.0, description="50 gallon gas water heater"),
            Material(name="Water Heater Tankless", category="plumbing", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=1800.00, waste_factor=0.0, description="Tankless gas water heater"),
            Material(name="Copper Pipe 3/4 inch Type L", category="plumbing", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.LF, unit_cost=5.50, waste_factor=0.08, description="Copper water supply pipe"),
            Material(name="PEX Tubing 3/4 inch", category="plumbing", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.LF, unit_cost=1.25, waste_factor=0.05, description="Cross-linked polyethylene tubing"),
            Material(name="PVC Pipe 3 inch DWV", category="plumbing", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.LF, unit_cost=4.50, waste_factor=0.05, description="Schedule 40 drain waste vent"),
            Material(name="Toilet (Standard)", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=250.00, waste_factor=0.0, description="1.28 GPF elongated toilet"),
            Material(name="Bathroom Vanity 36 inch", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=450.00, waste_factor=0.0, description="Vanity with top and faucet"),
            Material(name="Bathtub (Fiberglass)", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=350.00, waste_factor=0.0, description="60 inch fiberglass tub"),
            Material(name="Kitchen Sink (Stainless)", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=275.00, waste_factor=0.0, description="33 inch double bowl stainless"),
            Material(name="Kitchen Faucet", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=185.00, waste_factor=0.0, description="Single-handle pull-down faucet"),
            Material(name="Shower Valve Trim Kit", category="plumbing fixtures", csi_division=CSIDivision.DIV_15_MECHANICAL, unit=UnitType.EA, unit_cost=165.00, waste_factor=0.0, description="Pressure-balance shower valve"),
        ])

        # ── Division 16: Electrical ──
        materials.extend([
            Material(name="Electrical Panel 200 Amp", category="electrical", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=350.00, waste_factor=0.0, description="200A main breaker panel"),
            Material(name="Circuit Breaker 20 Amp", category="electrical", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=8.50, waste_factor=0.0, description="Single pole breaker"),
            Material(name="Circuit Breaker GFCI 20A", category="electrical", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=42.00, waste_factor=0.0, description="Ground fault circuit breaker"),
            Material(name="Romex 12/2 NM-B", category="wiring", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.LF, unit_cost=0.65, waste_factor=0.10, description="12 AWG 2-conductor NM cable"),
            Material(name="Romex 14/2 NM-B", category="wiring", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.LF, unit_cost=0.45, waste_factor=0.10, description="14 AWG 2-conductor NM cable"),
            Material(name="Duplex Receptacle 15A", category="devices", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=1.50, waste_factor=0.05, description="Standard duplex outlet"),
            Material(name="GFCI Receptacle 20A", category="devices", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=18.00, waste_factor=0.0, description="Ground fault outlet"),
            Material(name="Light Switch Single Pole", category="devices", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=1.75, waste_factor=0.05, description="Single pole toggle switch"),
            Material(name="LED Recessed Light 6 inch", category="lighting", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=22.00, waste_factor=0.0, description="IC-rated LED recessed can"),
            Material(name="Ceiling Fan with Light", category="lighting", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=185.00, waste_factor=0.0, description="52 inch ceiling fan with LED"),
            Material(name="Exterior Wall Sconce", category="lighting", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=65.00, waste_factor=0.0, description="LED exterior wall light"),
            Material(name="Smoke Detector (Hardwired)", category="safety", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=28.00, waste_factor=0.0, description="Hardwired with battery backup"),
            Material(name="Doorbell (Smart)", category="devices", csi_division=CSIDivision.DIV_16_ELECTRICAL, unit=UnitType.EA, unit_cost=150.00, waste_factor=0.0, description="Wi-Fi video doorbell"),
        ])

        return materials

    def count(self) -> int:
        """Total number of materials in the database."""
        return len(self._materials)

    def list_categories(self) -> list[str]:
        """Get all unique material categories."""
        return sorted(set(m.category for m in self._materials))

    def list_divisions(self) -> list[CSIDivision]:
        """Get all divisions that have materials."""
        return sorted(set(m.csi_division for m in self._materials), key=lambda d: d.value)
