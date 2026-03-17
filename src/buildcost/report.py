"""Report generation for construction cost estimates using Rich tables."""

from __future__ import annotations

import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from buildcost.models import CostEstimate


class CostReportGenerator:
    """Generates rich terminal reports for construction cost estimates."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def print_full_report(self, estimate: CostEstimate) -> None:
        """Print a complete cost report."""
        self.print_project_summary(estimate)
        self.print_cost_split(estimate)
        self.print_division_breakdown(estimate)
        self.print_top_line_items(estimate)
        if estimate.contingencies:
            self.print_contingencies(estimate)
        self.print_total_summary(estimate)

    def print_project_summary(self, estimate: CostEstimate) -> None:
        """Print project summary panel."""
        summary = (
            f"Project: {estimate.project_name}\n"
            f"Type: {estimate.project_type.value.title()}\n"
            f"Region: {estimate.region.value.title()}\n"
            f"Square Footage: {estimate.square_footage:,.0f} sq ft\n"
            f"Stories: {estimate.stories}\n"
            f"Total Cost: ${estimate.total_cost:,.2f}\n"
            f"Cost per Sq Ft: ${estimate.cost_per_sqft:,.2f}"
        )
        self.console.print(Panel(summary, title="Project Summary", border_style="blue"))

    def print_cost_split(self, estimate: CostEstimate) -> None:
        """Print material/labor/equipment cost split."""
        table = Table(title="Cost Split")
        table.add_column("Category", style="cyan")
        table.add_column("Amount", justify="right")
        table.add_column("Percentage", justify="right")

        subtotal = estimate.subtotal
        if subtotal > 0:
            table.add_row(
                "Materials",
                f"${estimate.subtotal_material:,.2f}",
                f"{estimate.subtotal_material / subtotal * 100:.1f}%",
            )
            table.add_row(
                "Labor",
                f"${estimate.subtotal_labor:,.2f}",
                f"{estimate.subtotal_labor / subtotal * 100:.1f}%",
            )
            table.add_row(
                "Equipment",
                f"${estimate.subtotal_equipment:,.2f}",
                f"{estimate.subtotal_equipment / subtotal * 100:.1f}%",
            )
            table.add_row(
                "[bold]Subtotal[/]",
                f"[bold]${subtotal:,.2f}[/]",
                "[bold]100.0%[/]",
            )

        self.console.print(table)

    def print_division_breakdown(self, estimate: CostEstimate) -> None:
        """Print cost breakdown by CSI division."""
        table = Table(title="Cost by CSI Division")
        table.add_column("Division", style="cyan")
        table.add_column("Material", justify="right")
        table.add_column("Labor", justify="right")
        table.add_column("Equipment", justify="right")
        table.add_column("Total", justify="right", style="bold")
        table.add_column("%", justify="right")

        subtotal = estimate.subtotal
        for dc in sorted(estimate.division_costs, key=lambda d: d.total_cost, reverse=True):
            if dc.total_cost == 0:
                continue
            pct = (dc.total_cost / subtotal * 100) if subtotal else 0
            table.add_row(
                dc.division.value,
                f"${dc.material_cost:,.0f}",
                f"${dc.labor_cost:,.0f}",
                f"${dc.equipment_cost:,.0f}",
                f"${dc.total_cost:,.0f}",
                f"{pct:.1f}%",
            )

        self.console.print(table)

    def print_top_line_items(self, estimate: CostEstimate, n: int = 15) -> None:
        """Print top N most expensive line items."""
        table = Table(title=f"Top {n} Cost Items")
        table.add_column("Description", style="cyan")
        table.add_column("Category")
        table.add_column("Qty", justify="right")
        table.add_column("Unit")
        table.add_column("Unit Cost", justify="right")
        table.add_column("Total", justify="right", style="bold")

        sorted_items = sorted(estimate.line_items, key=lambda x: x.total_cost, reverse=True)
        for item in sorted_items[:n]:
            table.add_row(
                item.description,
                item.category.title(),
                f"{item.quantity:,.1f}",
                item.unit.value,
                f"${item.unit_cost:,.2f}",
                f"${item.total_cost:,.2f}",
            )

        self.console.print(table)

    def print_contingencies(self, estimate: CostEstimate) -> None:
        """Print contingency breakdown."""
        table = Table(title="Contingencies")
        table.add_column("Item", style="cyan")
        table.add_column("Percentage", justify="right")
        table.add_column("Amount", justify="right")
        table.add_column("Reason", style="dim")

        for c in estimate.contingencies:
            table.add_row(
                c.name,
                f"{c.percentage:.1f}%",
                f"${c.amount:,.2f}",
                c.reason[:60],
            )

        table.add_row(
            "[bold]Total Contingency[/]",
            "",
            f"[bold]${estimate.contingency_total:,.2f}[/]",
            "",
        )

        self.console.print(table)

    def print_total_summary(self, estimate: CostEstimate) -> None:
        """Print final total summary."""
        summary = (
            f"Construction Subtotal:  ${estimate.subtotal:>12,.2f}\n"
            f"Contingencies:          ${estimate.contingency_total:>12,.2f}\n"
            f"{'─' * 42}\n"
            f"TOTAL ESTIMATED COST:   ${estimate.total_cost:>12,.2f}\n"
            f"Cost per Square Foot:   ${estimate.cost_per_sqft:>12,.2f}"
        )
        self.console.print(Panel(summary, title="Total Estimate", border_style="green"))

    def to_json(self, estimate: CostEstimate) -> str:
        """Export estimate as JSON string."""
        return estimate.model_dump_json(indent=2)

    def save_json(self, estimate: CostEstimate, filepath: str) -> None:
        """Save estimate as JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json(estimate))
