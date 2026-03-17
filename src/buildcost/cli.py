"""CLI interface for BuildCost construction cost estimator."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from buildcost.estimator.calculator import CostCalculator
from buildcost.estimator.materials import MaterialDatabase
from buildcost.estimator.labor import LaborRateDatabase
from buildcost.analyzer.breakdown import CostBreakdown
from buildcost.analyzer.comparator import CostComparator
from buildcost.models import ProjectType, Region
from buildcost.report import CostReportGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """BuildCost - Construction Cost Estimator."""
    pass


@cli.command()
@click.option("--sqft", type=float, required=True, help="Total square footage.")
@click.option("--type", "project_type", type=click.Choice(["residential", "commercial", "industrial", "institutional", "renovation"]), default="residential")
@click.option("--stories", type=int, default=1, help="Number of stories.")
@click.option("--region", type=click.Choice(["northeast", "southeast", "midwest", "southwest", "west", "northwest"]), default="southeast")
@click.option("--name", default="Construction Project", help="Project name.")
@click.option("--output", "-o", type=click.Path(), help="Save JSON report to file.")
def estimate(sqft: float, project_type: str, stories: int, region: str, name: str, output: str):
    """Generate a construction cost estimate."""
    try:
        calculator = CostCalculator()
        est = calculator.estimate(
            square_footage=sqft,
            project_type=project_type,
            stories=stories,
            region=region,
            project_name=name,
        )

        reporter = CostReportGenerator(console)
        reporter.print_full_report(est)

        if output:
            reporter.save_json(est, output)
            console.print(f"\n[green]Report saved to {output}[/]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option("--search", "-s", type=str, help="Search materials by name or category.")
@click.option("--division", "-d", type=str, help="Filter by CSI division number (e.g., '03').")
def materials(search: str, division: str):
    """Browse the material database."""
    db = MaterialDatabase()

    if search:
        results = db.search(search)
    else:
        results = db.materials

    if not results:
        console.print("[yellow]No materials found.[/]")
        return

    from rich.table import Table
    table = Table(title=f"Materials ({len(results)} found)")
    table.add_column("Name", style="cyan")
    table.add_column("Category")
    table.add_column("Division")
    table.add_column("Unit")
    table.add_column("Unit Cost", justify="right", style="green")

    for m in results[:50]:
        table.add_row(
            m.name, m.category, m.csi_division.value[:6],
            m.unit.value, f"${m.unit_cost:,.2f}",
        )

    console.print(table)
    console.print(f"\nTotal materials in database: {db.count()}")


@cli.command()
@click.option("--sqft", type=float, required=True, help="Total square footage.")
@click.option("--type", "project_type", type=click.Choice(["residential", "commercial", "industrial", "institutional", "renovation"]), default="residential")
@click.option("--region", type=click.Choice(["northeast", "southeast", "midwest", "southwest", "west", "northwest"]), default="southeast")
def compare(sqft: float, project_type: str, region: str):
    """Compare estimate against industry benchmarks."""
    calculator = CostCalculator()
    est = calculator.estimate(
        square_footage=sqft, project_type=project_type, region=region,
    )

    comparator = CostComparator()
    result = comparator.compare_to_benchmark(est)

    from rich.table import Table

    # Benchmark comparison
    table = Table(title="Benchmark Comparison")
    table.add_column("Tier", style="cyan")
    table.add_column("Benchmark $/sqft", justify="right")
    table.add_column("Status", justify="center")

    for tier, cost in result["benchmarks"].items():
        status = "[green]<-- Your estimate[/]" if tier == result["quality_tier"] else ""
        table.add_row(tier.title(), f"${cost:,.2f}", status)

    console.print(table)

    console.print(f"\nYour cost: [bold]${result['cost_per_sqft']:,.2f}/sqft[/]")
    console.print(f"Quality tier: [bold]{result['quality_tier'].title()}[/]")
    console.print(f"Variance from standard: [bold]{result['variance_from_standard_pct']:+.1f}%[/]")


@cli.command()
@click.option("--sqft", type=float, required=True)
@click.option("--type", "project_type", type=click.Choice(["residential", "commercial", "industrial", "institutional", "renovation"]), default="residential")
@click.option("--stories", type=int, default=1)
@click.option("--output", "-o", type=click.Path(), help="Output JSON file path.")
def report(sqft: float, project_type: str, stories: int, output: str):
    """Generate a full cost report."""
    calculator = CostCalculator()
    est = calculator.estimate(
        square_footage=sqft, project_type=project_type, stories=stories,
    )

    reporter = CostReportGenerator(console)
    reporter.print_full_report(est)

    # Also show benchmark comparison
    comparator = CostComparator()
    benchmark = comparator.compare_to_benchmark(est)
    console.print(f"\nBenchmark tier: [bold]{benchmark['quality_tier'].title()}[/] ({benchmark['position']})")

    if output:
        reporter.save_json(est, output)
        console.print(f"\n[green]Report saved to {output}[/]")


if __name__ == "__main__":
    cli()
