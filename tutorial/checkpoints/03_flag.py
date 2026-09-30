import typer


def label(item: str, quantity: int = 1, uppercase: bool = False):
    """Print a cargo label."""
    if uppercase:
        item = item.upper()
    typer.echo(f"Cargo: {item}")
    typer.echo(f"Units: {quantity}")


if __name__ == "__main__":
    typer.run(label)
