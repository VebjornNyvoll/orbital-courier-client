from pathlib import Path
from typing import Annotated

import typer

from report_data import summarize_csv


def summarize(
    source: Annotated[Path, typer.Argument(help="CSV file with a header row.")],
):
    """Show the row count and column names of a CSV file.

    Example: uv run python main.py data/tickets.csv
    """
    report = summarize_csv(source)
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    typer.run(summarize)
