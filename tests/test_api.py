import json
from zipfile import ZipFile

import httpx
import pytest

import export_submission
from game_api import GameClient, GameError


def test_retry_reuses_mutation_key():
    keys = []

    def handler(request):
        keys.append(request.headers["Idempotency-Key"])
        if len(keys) == 1:
            raise httpx.ReadTimeout("response lost")
        return httpx.Response(200, json={"score": 10})

    api = GameClient("https://game.test", "test", transport=httpx.MockTransport(handler))
    assert api.deliver("P01")["score"] == 10
    assert len(keys) == 2 and keys[0] == keys[1]


def test_join_is_not_retried():
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("response lost")

    api = GameClient("https://game.test", transport=httpx.MockTransport(handler))
    with pytest.raises(GameError) as error:
        api.join("Alex", "code")
    assert len(calls) == 1
    assert calls[0].extensions["timeout"]["read"] == 30.0
    assert error.value.code == "timeout"
    assert "recover your token before retrying" in error.value.hint


def test_readiness_allows_a_cold_start():
    def handler(request):
        assert request.method == "GET" and request.url.path == "/health"
        assert request.extensions["timeout"]["read"] == 120.0
        assert request.extensions["timeout"]["connect"] == 15.0
        return httpx.Response(200, json={"status": "ok"})

    api = GameClient("https://game.test", transport=httpx.MockTransport(handler))
    assert api.wait_until_ready() == {"status": "ok"}


def test_missing_scheme_explains_how_to_fix_url():
    with pytest.raises(GameError) as error:
        GameClient("orbital-courier.onrender.com")
    assert error.value.code == "configuration"
    assert "Include https://" in error.value.hint


@pytest.mark.parametrize(
    "detail",
    [
        "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer",
        "[Errno -2] Name or service not known",
        "[Errno 111] Connection refused",
    ],
)
def test_connection_errors_preserve_diagnostic_detail(detail):
    def handler(request):
        raise httpx.ConnectError(detail)

    api = GameClient("https://game.test", transport=httpx.MockTransport(handler))
    with pytest.raises(GameError) as error:
        api.wait_until_ready()
    assert f"Connection detail: ConnectError: {detail}" in error.value.hint
    assert "No registration was submitted" in error.value.hint


def test_proxy_error_does_not_expose_url_credentials():
    def handler(request):
        raise httpx.ProxyError("Could not connect to http://user:private-password@proxy.test:8080")

    api = GameClient("https://game.test", transport=httpx.MockTransport(handler))
    with pytest.raises(GameError) as error:
        api.wait_until_ready()
    assert "ProxyError" in error.value.hint
    assert "private-password" not in error.value.hint


def test_api_failure_has_recovery_hint():
    def handler(request):
        return httpx.Response(
            409, json={"error": {"code": "cargo_full", "message": "Full", "hint": "Unload first"}}
        )

    api = GameClient("https://game.test", transport=httpx.MockTransport(handler))
    with pytest.raises(GameError) as error:
        api.load_cargo("food", 2)
    assert error.value.hint == "Unload first"
    assert error.value.status == 409


def test_config_overrides_and_missing(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.delenv("ORBITAL_URL", raising=False)
    monkeypatch.delenv("ORBITAL_TOKEN", raising=False)
    with pytest.raises(GameError):
        GameClient.from_config(path)
    path.write_text(json.dumps({"url": "http://file.test", "token": "file-token"}))
    monkeypatch.setenv("ORBITAL_URL", "https://env.test")
    api = GameClient.from_config(path)
    assert api.base_url == "https://env.test" and api.token == "file-token"


def test_export_excludes_credentials_and_dependencies(tmp_path, monkeypatch):
    for name in ["cli.py", "USAGE.md", ".player.json", ".env", "game_api.py"]:
        (tmp_path / name).write_text("secret" if name.startswith(".") else "content")
    monkeypatch.setattr(export_submission, "ROOT", tmp_path)
    archive = export_submission.export(tmp_path / "submission.zip")
    with ZipFile(archive) as file:
        assert set(file.namelist()) == {"cli.py", "USAGE.md"}
