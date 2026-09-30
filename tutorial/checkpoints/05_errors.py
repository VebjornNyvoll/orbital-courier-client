from pathlib import Path
from typing import Annotated

import typer
from report_data import SummaryError, summarize_csv


def summarize(
    source: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True, help="CSV file with a header row.")],
    encoding: Annotated[str, typer.Option(help="Character encoding of the CSV file.")] = "utf-8",
):
    """Count data rows and show the column names in a CSV file.

    Example: uv run python main.py data/tickets.csv
    """
    try:
        report = summarize_csv(source, encoding=encoding)
    except SummaryError as exc:
        typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
        raise typer.Exit(1) from None
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    typer.run(summarize)
