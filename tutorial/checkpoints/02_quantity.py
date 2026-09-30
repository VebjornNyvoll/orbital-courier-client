import typer


def label(item: str, quantity: int = 1):
    """Print a cargo label."""
    typer.echo(f"Cargo: {item}")
    typer.echo(f"Units: {quantity}")


if __name__ == "__main__":
    typer.run(label)
