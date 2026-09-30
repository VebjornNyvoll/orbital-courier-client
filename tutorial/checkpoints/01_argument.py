import typer


def label(item: str):
    """Print a cargo label."""
    typer.echo(f"Cargo: {item}")


if __name__ == "__main__":
    typer.run(label)
