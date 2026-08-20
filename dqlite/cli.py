"""Command-line interface for dq-lite."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from dqlite.core.engine import validate
from dqlite.core.result import ValidationResult

app = typer.Typer(
    name="dqlite",
    help="dq-lite: Lightweight data quality validation",
    add_completion=False,
)
console = Console()


@app.command()
def validate_csv(
    path: Path = typer.Argument(..., help="Path to CSV file"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="YAML config file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for report"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, json, markdown"),
):
    """Validate a CSV file against expectations."""
    import pandas as pd

    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)

    df = pd.read_csv(path)

    # If no config provided, run a basic suite
    if config is None:
        from dqlite import expect
        expectations = _build_default_expectations(df)
    else:
        expectations = _load_config(config)

    result = validate(df, expectations)

    # Output
    if format == "json":
        output_text = result.to_json()
    elif format == "markdown":
        output_text = result.to_markdown()
    else:
        output_text = None
        _print_rich_report(result)

    if output_text and output:
        output.write_text(output_text)
        console.print(f"[green]Report saved to[/green] {output}")
    elif output_text:
        console.print(output_text)

    if not result.success:
        raise typer.Exit(1)


def _build_default_expectations(df):
    """Build a sensible default expectation suite."""
    from dqlite import expect
    from dqlite.expectations.table import expect_table

    expectations = []

    # Table-level
    expectations.append(expect_table().row_count().greater_than(0))

    # Column-level: check each column for nulls
    for col in df.columns:
        null_pct = df[col].isna().mean()
        if null_pct == 0:
            expectations.append(expect(col).not_null())
        elif null_pct < 0.1:
            expectations.append(expect(col).not_null())  # Flag it

    return expectations


def _load_config(config_path: Path):
    """Load expectations from YAML config."""
    import yaml
    from dqlite import expect
    from dqlite.core.registry import ExpectationRegistry

    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    expectations = []
    for item in cfg.get("expectations", []):
        exp_type = item["type"]
        column = item.get("column")
        kwargs = item.get("kwargs", {})

        if exp_type == "not_null":
            expectations.append(expect(column).not_null())
        elif exp_type == "between":
            expectations.append(expect(column).between(**kwargs))
        elif exp_type == "unique":
            expectations.append(expect(column).unique())
        elif exp_type == "in_set":
            expectations.append(expect(column).in_set(kwargs["allowed"]))
        elif exp_type == "matches_regex":
            expectations.append(expect(column).matches_regex(kwargs["pattern"]))

    return expectations


def _print_rich_report(result: ValidationResult):
    """Print a beautiful terminal report."""
    color = "green" if result.success else "red"
    status = "PASS ✅" if result.success else "FAIL ❌"

    console.print(Panel.fit(
        f"[bold {color}]{status}[/bold {color}]  |  "
        f"{result.statistics['evaluated_expectations']} checks  |  "
        f"{result.statistics['evaluation_time_seconds']}s",
        title="dq-lite Report",
        border_style=color,
    ))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Expectation", style="cyan")
    table.add_column("Column", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Unexpected", justify="right")
    table.add_column("Details", style="dim")

    for r in result.results:
        status_icon = "[green]✓[/green]" if r.success else "[red]✗[/red]"
        col = r.column or "-"
        details = str(r.details)[:40]
        table.add_row(
            r.expectation_type,
            col,
            status_icon,
            str(r.unexpected_count),
            details,
        )

    console.print(table)


@app.command()
def init(
    path: Path = typer.Argument(Path("dqlite.yaml"), help="Config file path"),
):
    """Generate a starter configuration file."""
    template = """# dq-lite configuration
# docs: https://github.com/yourname/dq-lite

dataset:
  type: csv
  path: data.csv

expectations:
  - type: row_count_greater_than
    kwargs:
      threshold: 0

  - type: not_null
    column: user_id

  - type: between
    column: age
    kwargs:
      min_val: 0
      max_val: 120

  - type: matches_regex
    column: email
    kwargs:
      pattern: ".+@.+\..+"
"""
    path.write_text(template)
    console.print(f"[green]Created starter config:[/green] {path}")


if __name__ == "__main__":
    app()
