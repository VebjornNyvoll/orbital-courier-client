"""Part 1 starts here. Follow the slides and evolve this function."""

import typer


def hello(name: str):
    """Greet a fellow courier."""
    typer.echo(f"Hello, {name}!")


if __name__ == "__main__":
    typer.run(hello)
