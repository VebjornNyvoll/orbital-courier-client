"""Her lager du CLI-et ditt. Spilleregler og tilgjengelige funksjoner står i README.md."""

import json
import sys
from typing import Annotated

import typer

from verktoy.api import GameClient, GameError

app = typer.Typer(no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


@app.callback()
def main():
    """Kometfrakteratene: fly mellom stasjoner og lever last.

    Prøv: uv run python cli.py status
    """


@app.command()
def status(
    as_json: Annotated[bool, typer.Option("--json", help="Vis resultatet som JSON.")] = False,
):
    """Se hvor du er, hva du har i skipet og hvor mange poeng du har."""
    try:
        # Lag klienten inne i kommandoen, så --help virker uten kontakt med serveren.
        game = GameClient.from_config()
        state = game.status()
    except GameError as exc:
        print(f"Feil: {exc.message}\n{exc.hint}", file=sys.stderr)
        raise typer.Exit(1) from None
    if as_json:
        print(json.dumps(state))
    else:
        print(f"{state['name']} på {state['location']} ({state['mode']})")
        print(f"Poeng: {state['score']}  Last: {state['cargo'] or 'tomt'}")


# Legg til kommandoene dine her. Bruk status som eksempel på oppsett og feilhåndtering.
# F.eks. gir game.list_contracts(status="open") en dict med lista data["contracts"].
# game.travel("luna") flytter skipet. Du bestemmer hvordan kommandoen skal se ut.
# Skriv hjelpetekst og brukseksempler i docstringene, så de dukker opp i --help.

if __name__ == "__main__":
    app()
