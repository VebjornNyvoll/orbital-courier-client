"""Provided workshop infrastructure. You only need the named methods below.

Methods return ordinary dictionaries. Expected failures raise GameError with
code, message, and hint. Configuration lives beside this file, never in a submission.
"""

import json
import os
import uuid
from pathlib import Path
from urllib.parse import quote, urlparse

import httpx

CONFIG_PATH = Path(__file__).with_name(".player.json")


class GameError(Exception):
    def __init__(self, code: str, message: str, hint: str = "", status: int = 0):
        self.code, self.message, self.hint, self.status = code, message, hint, status
        super().__init__(message)


def validate_url(url: str) -> str:
    url = url.strip()
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise GameError(
            "configuration", "Server URL must be an http(s) address without credentials.",
            "Include https://, for example https://orbital-courier.onrender.com.",
        )
    if parsed.query or parsed.fragment:
        raise GameError("configuration", "Server URL cannot include a query or fragment.")
    return url.rstrip("/")


class GameClient:
    def __init__(self, base_url: str, token: str = "", *, transport=None):
        self.base_url = validate_url(base_url)
        self.token = token
        self.transport = transport

    @classmethod
    def from_config(cls, path: Path = CONFIG_PATH):
        """Environment variables ORBITAL_URL and ORBITAL_TOKEN override the local file."""
        try:
            saved = json.loads(path.read_text()) if path.exists() else {}
            if not isinstance(saved, dict):
                raise ValueError("configuration must be an object")
        except (OSError, ValueError):
            raise GameError(
                "configuration",
                "Cannot read player configuration.",
                "Run uv run python setup_player.py to repair it.",
            ) from None
        url = os.environ.get("ORBITAL_URL") or saved.get("url")
        token = os.environ.get("ORBITAL_TOKEN") or saved.get("token")
        if not isinstance(url, str) or not isinstance(token, str) or not url or not token:
            raise GameError(
                "configuration",
                "Player configuration is missing.",
                "Run uv run python setup_player.py first.",
            )
        return cls(url, token)

    def _request(self, method, path, *, body=None, params=None, timeout=5.0):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        if method == "POST" and path != "/api/join":
            headers["Idempotency-Key"] = str(uuid.uuid4())
        # A retry uses the same key. Joining is deliberately never retried automatically.
        attempts = 1 if path in {"/api/join", "/health"} else 2
        with httpx.Client(timeout=timeout, transport=self.transport, follow_redirects=False) as client:
            for attempt in range(attempts):
                try:
                    response = client.request(
                        method, self.base_url + path, json=body, params=params, headers=headers
                    )
                    break
                except httpx.TransportError as exc:
                    if attempt + 1 == attempts:
                        hint = (
                            "Check the full server URL and the VM's internet connection."
                        )
                        if path == "/api/join":
                            hint += (
                                " Registration may have reached the server. Ask the instructor"
                                " to check your display name and recover your token before retrying."
                            )
                        elif path == "/health":
                            hint += " No registration was submitted; you can rerun setup."
                        else:
                            hint += " Check status before repeating an action."
                        timed_out = isinstance(exc, httpx.TimeoutException)
                        raise GameError(
                            "timeout" if timed_out else "connection",
                            "The game server did not respond in time."
                            if timed_out else "Could not connect to the game server.",
                            hint,
                        ) from None
        try:
            data = response.json()
        except ValueError:
            raise GameError(
                "invalid_response",
                "The server returned an unexpected response.",
                "Check your server URL or ask the instructor.",
                response.status_code,
            ) from None
        if not response.is_success:
            error = data.get("error", {}) if isinstance(data, dict) else {}
            raise GameError(
                error.get("code", "http_error"),
                error.get("message", "Request failed."),
                error.get("hint", "Ask the instructor for help."),
                response.status_code,
            )
        if not isinstance(data, dict):
            raise GameError("invalid_response", "Expected a JSON object from the server.")
        return data

    def get(self, path: str, **params):
        """Low-level GET example. Prefer the named game methods in your CLI."""
        return self._request("GET", path, params=params)

    def post(self, path: str, **body):
        """Low-level POST with a request key for safe network retries."""
        return self._request("POST", path, body=body)

    def put(self, path: str, **body):
        return self._request("PUT", path, body=body)

    def join(self, name: str, join_code: str):
        return self._request(
            "POST", "/api/join", body={"name": name, "join_code": join_code}, timeout=30.0
        )

    def wait_until_ready(self):
        """Wake a sleeping host with a read-only request before submitting registration."""
        data = self._request("GET", "/health", timeout=httpx.Timeout(120.0, connect=15.0))
        if data.get("status") != "ok":
            raise GameError(
                "unavailable", "The game server is not ready.",
                "No registration was submitted. Check the server URL or ask the instructor.",
            )
        return data

    def session(self):
        return self.get("/api/session")

    def status(self):
        return self.get("/api/me")

    def map(self):
        return self.get("/api/map")

    def list_contracts(self, status: str = "all"):
        return self.get("/api/contracts", status=status)

    def get_contract(self, contract_id: str):
        return self.get(f"/api/contracts/{quote(contract_id, safe='')}")

    def travel(self, destination: str):
        return self.post("/api/travel", destination=destination)

    def load_cargo(self, item: str, quantity: int = 1):
        return self.post("/api/cargo/load", item=item, quantity=quantity)

    def unload_cargo(self, item: str, quantity: int = 1):
        return self.post("/api/cargo/unload", item=item, quantity=quantity)

    def deliver(self, contract_id: str):
        return self.post(f"/api/contracts/{quote(contract_id, safe='')}/deliver")

    def reset_practice(self):
        return self.post("/api/practice/reset")

    def rename(self, name: str):
        return self.put("/api/me/profile", name=name)
