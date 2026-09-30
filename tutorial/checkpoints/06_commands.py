from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def label(
    item: str,
    quantity: Annotated[
        int, typer.Option(min=1, max=6, help="Number of cargo units.")
    ] = 1,
    uppercase: bool = False,
):
    """Print a cargo label. Example: label food --quantity 2."""
    if uppercase:
        item = item.upper()
    typer.echo(f"Cargo: {item}")
    typer.echo(f"Units: {quantity}")


@app.command()
def items():
    """List the cargo names used in the game."""
    typer.echo("food, water, tools, medicine, fuel, parts")


if __name__ == "__main__":
    app()
