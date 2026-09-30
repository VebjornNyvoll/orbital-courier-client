from pathlib import Path

import typer

from report_data import summarize_csv


def summarize(source: Path, encoding: str = "utf-8"):
    report = summarize_csv(source, encoding=encoding)
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    typer.run(summarize)
