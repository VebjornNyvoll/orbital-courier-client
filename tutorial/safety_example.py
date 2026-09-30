"""Reference: call this guard before an operation that would overwrite a file."""
import sys
from pathlib import Path

import typer


def confirm_replace(output: Path, yes: bool = False):
    if not output.exists() or yes:
        return
    if not sys.stdin.isatty():
        typer.echo("File exists. Use --yes to allow replacement.", err=True)
        raise typer.Exit(2)
    typer.confirm(f"Replace {output}?", abort=True, err=True)
