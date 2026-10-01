import json

import httpx
import pytest
import typer
from typer.testing import CliRunner

from verktoy import oppsett as setup_player
from verktoy.api import GameClient


@pytest.mark.parametrize("failure", [None, httpx.ReadTimeout, httpx.ConnectError])
def test_setup_checks_readiness_before_registering(tmp_path, monkeypatch, failure):
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path == "/health":
            if failure:
                raise failure("unavailable")
            return httpx.Response(200, json={"status": "ok"})
        assert request.url.path == "/api/join"
        assert json.loads(request.content) == {"name": "Alex", "join_code": "ws"}
        return httpx.Response(201, json={"name": "Alex", "token": "test-token"})

    config = tmp_path / ".player.json"
    monkeypatch.setattr(setup_player, "CONFIG_PATH", config)
    monkeypatch.delenv("ORBITAL_URL", raising=False)
    monkeypatch.setattr(
        setup_player, "GameClient",
        lambda url: GameClient(url, transport=httpx.MockTransport(handler)),
    )
    app = typer.Typer()
    app.command()(setup_player.main)
    result = CliRunner().invoke(app, [], input="\nn\nAlex\nws\n")
    assert requests[0].url.host == "orbital-courier.onrender.com"
    if failure:
        assert result.exit_code == 1
        assert len(requests) == 1
        assert not config.exists()
        assert "Ingen registrering er sendt" in result.stderr
        assert "Navn i spillet" not in result.output
    else:
        assert result.exit_code == 0, result.output
        assert [r.method for r in requests] == ["GET", "POST"]
        assert json.loads(config.read_text()) == {
            "url": "https://orbital-courier.onrender.com", "token": "test-token", "name": "Alex"
        }
        assert "test-token" not in result.output
