"""Provided setup utility. Keep your attention on cli.py during the workshop."""

import json
import os
import tempfile

import typer

from game_api import CONFIG_PATH, GameClient, GameError


def main():
    """Register once, or configure an existing participant token."""
    try:
        if CONFIG_PATH.exists():
            typer.confirm("Replace this checkout's saved player configuration?", abort=True)
        url = typer.prompt(
            "Server URL",
            default=os.environ.get("ORBITAL_URL") or "https://orbital-courier.onrender.com",
        )
        api = GameClient(url)
        typer.echo("Checking the server. A sleeping free host can take up to two minutes to respond.")
        api.wait_until_ready()
        existing = typer.confirm("Do you already have a participant token?", default=False)
        if existing:
            token = typer.prompt("Participant token", hide_input=True)
            info = GameClient(url, token).status()
        else:
            name = typer.prompt("Display name")
            code = typer.prompt("Workshop join code", hide_input=True)
            info = api.join(name, code)
            token = info["token"]
        content = json.dumps({"url": api.base_url, "token": token, "name": info["name"]}, indent=2)
        # Atomic replacement avoids half-written credentials. File is excluded from Git and exports.
        fd, temporary = tempfile.mkstemp(dir=CONFIG_PATH.parent, prefix=".player.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(content + "\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, CONFIG_PATH)
        typer.echo(f"Ready, {info['name']}. Run: uv run python cli.py status")
    except GameError as exc:
        typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
        raise typer.Exit(1) from None
    except OSError:
        typer.echo(
            "Could not save configuration. Ask the instructor for token recovery if you just registered.",
            err=True,
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    typer.run(main)
