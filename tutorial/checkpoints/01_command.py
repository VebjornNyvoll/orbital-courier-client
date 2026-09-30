from pathlib import Path

import typer

from report_data import summarize_csv


def summarize(source: Path):
    """Show the row count and column names of a CSV file."""
    report = summarize_csv(source)
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    typer.run(summarize)
