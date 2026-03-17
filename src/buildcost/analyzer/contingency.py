"""Contingency calculator adding risk-based contingencies to estimates.

Construction projects face various risks that can increase costs. This module
calculates appropriate contingency amounts based on project type, complexity,
and risk factors.
"""

from __future__ import annotations

from buildcost.models import ContingencyItem, ProjectType


# Base contingency percentages by project type
BASE_CONTINGENCY: dict[ProjectType, float] = {
    ProjectType.RESIDENTIAL: 8.0,
    ProjectType.COMMERCIAL: 10.0,
    ProjectType.INDUSTRIAL: 12.0,
    ProjectType.INSTITUTIONAL: 10.0,
    ProjectType.RENOVATION: 15.0,
}

# Additional risk factors
RISK_FACTORS: dict[str, dict] = {
    "multi_story": {
        "name": "Multi-Story Complexity",
        "description": "Additional risk for buildings with multiple stories",
        "percentage_per_story": 1.5,
        "max_percentage": 8.0,
    },
    "market_volatility": {
        "name": "Material Price Volatility",
        "description": "Buffer for material price fluctuations in current market",
        "percentage": 3.0,
    },
    "design_changes": {
        "name": "Design Change Allowance",
        "description": "Allowance for owner-initiated design changes during construction",
        "percentage": 2.0,
    },
    "weather_delays": {
        "name": "Weather Delay Allowance",
        "description": "Buffer for weather-related construction delays",
        "percentage": 1.5,
    },
    "permit_compliance": {
        "name": "Permit & Code Compliance",
        "description": "Potential costs from code changes or inspection requirements",
        "percentage": 1.0,
    },
}


class ContingencyCalculator:
    """Calculates risk-based contingency amounts for construction estimates.

    Contingency types:
    1. Base construction contingency (by project type)
    2. Multi-story complexity premium
    3. Material price volatility buffer
    4. Design change allowance
    5. Weather delay allowance
    6. Permit & code compliance buffer
    """

    def calculate(
        self,
        subtotal: float,
        project_type: ProjectType | str,
        stories: int = 1,
        include_volatility: bool = True,
        include_design_changes: bool = True,
        include_weather: bool = True,
        include_permits: bool = True,
    ) -> list[ContingencyItem]:
        """Calculate contingency line items.

        Args:
            subtotal: The construction subtotal before contingencies.
            project_type: Type of project.
            stories: Number of stories.
            include_volatility: Include material price volatility.
            include_design_changes: Include design change allowance.
            include_weather: Include weather delay allowance.
            include_permits: Include permit compliance allowance.

        Returns:
            List of ContingencyItem objects.
        """
        if isinstance(project_type, str):
            project_type = ProjectType(project_type.lower())

        items: list[ContingencyItem] = []

        # 1. Base contingency
        base_pct = BASE_CONTINGENCY.get(project_type, 10.0)
        items.append(ContingencyItem(
            name="Construction Contingency",
            percentage=base_pct,
            amount=round(subtotal * base_pct / 100, 2),
            reason=f"Standard {project_type.value} construction contingency",
        ))

        # 2. Multi-story premium
        if stories > 1:
            ms_info = RISK_FACTORS["multi_story"]
            pct = min(
                (stories - 1) * ms_info["percentage_per_story"],
                ms_info["max_percentage"],
            )
            items.append(ContingencyItem(
                name=ms_info["name"],
                percentage=round(pct, 1),
                amount=round(subtotal * pct / 100, 2),
                reason=f"{stories} stories - {ms_info['description']}",
            ))

        # 3. Material price volatility
        if include_volatility:
            vol = RISK_FACTORS["market_volatility"]
            items.append(ContingencyItem(
                name=vol["name"],
                percentage=vol["percentage"],
                amount=round(subtotal * vol["percentage"] / 100, 2),
                reason=vol["description"],
            ))

        # 4. Design change allowance
        if include_design_changes:
            dc = RISK_FACTORS["design_changes"]
            items.append(ContingencyItem(
                name=dc["name"],
                percentage=dc["percentage"],
                amount=round(subtotal * dc["percentage"] / 100, 2),
                reason=dc["description"],
            ))

        # 5. Weather delays
        if include_weather:
            wd = RISK_FACTORS["weather_delays"]
            items.append(ContingencyItem(
                name=wd["name"],
                percentage=wd["percentage"],
                amount=round(subtotal * wd["percentage"] / 100, 2),
                reason=wd["description"],
            ))

        # 6. Permit compliance
        if include_permits:
            pc = RISK_FACTORS["permit_compliance"]
            items.append(ContingencyItem(
                name=pc["name"],
                percentage=pc["percentage"],
                amount=round(subtotal * pc["percentage"] / 100, 2),
                reason=pc["description"],
            ))

        return items

    def get_total_contingency_pct(
        self, project_type: ProjectType, stories: int = 1,
    ) -> float:
        """Get the total contingency percentage for a project."""
        base = BASE_CONTINGENCY.get(project_type, 10.0)
        ms = min(
            max(0, (stories - 1) * RISK_FACTORS["multi_story"]["percentage_per_story"]),
            RISK_FACTORS["multi_story"]["max_percentage"],
        )
        volatility = RISK_FACTORS["market_volatility"]["percentage"]
        design = RISK_FACTORS["design_changes"]["percentage"]
        weather = RISK_FACTORS["weather_delays"]["percentage"]
        permits = RISK_FACTORS["permit_compliance"]["percentage"]
        return base + ms + volatility + design + weather + permits

    @staticmethod
    def get_risk_summary() -> dict[str, dict]:
        """Get a summary of all risk factors."""
        return RISK_FACTORS.copy()
