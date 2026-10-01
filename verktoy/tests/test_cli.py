import json

from typer.testing import CliRunner

import cli
from verktoy.api import GameError

runner = CliRunner()


def test_help_never_needs_server(monkeypatch):
    def unavailable(*args):
        raise AssertionError("Hjelpetekst skal virke uten nett")

    monkeypatch.setattr(cli.GameClient, "from_config", unavailable)
    for args in (["--help"], ["status", "--help"], ["-h"]):
        result = runner.invoke(cli.app, args)
        assert result.exit_code == 0
        assert "status" in result.output.lower()


def test_json_is_clean(monkeypatch):
    class Fake:
        def status(self):
            return {
                "name": "Alex",
                "location": "earth",
                "mode": "practice",
                "score": 0,
                "cargo": {},
            }

    monkeypatch.setattr(cli.GameClient, "from_config", lambda: Fake())
    result = runner.invoke(cli.app, ["status", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["location"] == "earth"
    assert not result.stderr


def test_errors_use_stderr_and_failure_exit(monkeypatch):
    def unavailable():
        raise GameError("connection", "Serveren er utilgjengelig.", "Sjekk nettforbindelsen.")

    monkeypatch.setattr(cli.GameClient, "from_config", unavailable)
    result = runner.invoke(cli.app, ["status"])
    assert result.exit_code == 1
    assert not result.stdout
    assert "Sjekk nettforbindelsen" in result.stderr
