import json

import httpx
import pytest

from verktoy.api import GameClient, GameError


def test_existing_root_config_is_found_from_another_directory(tmp_path, monkeypatch):
    from pathlib import Path
    from verktoy.api import CONFIG_PATH

    assert CONFIG_PATH == Path(__file__).resolve().parents[2] / ".player.json"
    original_read = Path.read_text
    original_exists = Path.exists
    monkeypatch.setattr(Path, "exists", lambda p: True if p == CONFIG_PATH else original_exists(p))
    monkeypatch.setattr(
        Path, "read_text",
        lambda p: json.dumps({"url": "https://game.test", "token": "saved-token"})
        if p == CONFIG_PATH else original_read(p),
    )
    monkeypatch.delenv("ORBITAL_URL", raising=False)
    monkeypatch.delenv("ORBITAL_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    api = GameClient.from_config()
    assert api.base_url == "https://game.test" and api.token == "saved-token"


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
    assert "gi deg et nytt token før du prøver igjen" in error.value.hint


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
    assert "Ta med https://" in error.value.hint


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
    assert f"Teknisk detalj: ConnectError: {detail}" in error.value.hint
    assert "Ingen registrering er sendt" in error.value.hint


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
