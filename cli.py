"""Your workshop CLI. Add commands here; game_api.py handles the network."""

import json
from typing import Annotated

import typer

from game_api import GameClient, GameError

app = typer.Typer(no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


@app.callback()
def main():
    """Kometfrakteratene: inspect your ship and complete deliveries.

    Start with: uv run python cli.py status
    """


@app.command()
def status(
    as_json: Annotated[bool, typer.Option("--json", help="Print JSON for scripts.")] = False,
):
    """Show your current location, cargo, and score."""
    try:
        state = GameClient.from_config().status()
    except GameError as exc:
        typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
        raise typer.Exit(1) from None
    if as_json:
        typer.echo(json.dumps(state))
    else:
        typer.echo(f"{state['name']} at {state['location']} ({state['mode']})")
        typer.echo(f"Score: {state['score']}  Cargo: {state['cargo'] or 'empty'}")


# Your turn: contracts, map, travel, load, deliver, unload, and reset.
# See docs/api-guide.md for every provided function and examples.

if __name__ == "__main__":
    app()
