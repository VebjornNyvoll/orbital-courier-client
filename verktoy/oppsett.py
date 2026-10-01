"""Ferdig oppsett av spillerkonto. Du trenger bare å jobbe i cli.py."""

import json
import os
import sys
import tempfile

import typer

from verktoy.api import CONFIG_PATH, GameClient, GameError


def main():
    """Registrer deg én gang, eller bruk et token du allerede har."""
    try:
        if CONFIG_PATH.exists():
            typer.confirm("Vil du bytte ut spilleroppsettet som er lagret her?", abort=True)
        url = typer.prompt(
            "Serveradresse",
            default=os.environ.get("ORBITAL_URL") or "https://orbital-courier.onrender.com",
        )
        api = GameClient(url)
        print("Sjekker serveren. Hvis den sover, kan det ta opptil to minutter før den svarer.")
        api.wait_until_ready()
        existing = typer.confirm("Har du allerede et spillertoken?", default=False)
        if existing:
            token = typer.prompt("Spillertoken", hide_input=True)
            info = GameClient(url, token).status()
        else:
            name = typer.prompt("Navn i spillet")
            code = typer.prompt("Workshop-kode", hide_input=True)
            info = api.join(name, code)
            token = info["token"]
        content = json.dumps({"url": api.base_url, "token": token, "name": info["name"]}, indent=2)
        # Bytt hele fila i én operasjon, så vi ikke lagrer et halvferdig token. Git ignorerer fila.
        fd, temporary = tempfile.mkstemp(dir=CONFIG_PATH.parent, prefix=".player.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(content + "\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, CONFIG_PATH)
        print(f"Klar, {info['name']}! Kjør: uv run python cli.py status")
    except GameError as exc:
        print(f"Feil: {exc.message}\n{exc.hint}", file=sys.stderr)
        raise typer.Exit(1) from None
    except OSError:
        print(
            "Kunne ikke lagre oppsettet. Be instruktøren om et nytt token hvis du nettopp registrerte deg.",
            file=sys.stderr,
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    typer.run(main)
