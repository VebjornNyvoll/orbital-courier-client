from typing import Annotated

import typer


def label(
    item: str,
    quantity: Annotated[
        int, typer.Option(min=1, max=6, help="Number of cargo units.")
    ] = 1,
    uppercase: bool = False,
):
    """Print a cargo label. Example: food --quantity 2."""
    if uppercase:
        item = item.upper()
    typer.echo(f"Cargo: {item}")
    typer.echo(f"Units: {quantity}")


if __name__ == "__main__":
    typer.run(label)
