"""Ferdig API-klient. Du bruker funksjonene fra cli.py.

Funksjonene returnerer vanlige dicts. Forventede feil gir GameError med code,
message og hint. Serveradresse og token lagres i .player.json i root i repoet.
"""

import json
import os
import re
import uuid
from pathlib import Path
from urllib.parse import quote, urlparse

import httpx

CONFIG_PATH = Path(__file__).resolve().parents[1] / ".player.json"


class GameError(Exception):
    def __init__(self, code: str, message: str, hint: str = "", status: int = 0):
        self.code, self.message, self.hint, self.status = code, message, hint, status
        super().__init__(message)


def connection_detail(exc: httpx.TransportError) -> str:
    """Vis nettverksfeilen uten å vise innloggingsinfo fra proxy-adresser."""
    detail = re.sub(r"[a-zA-Z][a-zA-Z0-9+.-]*://\S+", "[URL]", str(exc))
    detail = " ".join(detail.split())[:500]
    return f"Teknisk detalj: {type(exc).__name__}: {detail}"


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
            "configuration", "Serveradressen må starte med http:// eller https:// og være uten innloggingsinfo.",
            "Ta med https://, f.eks. https://orbital-courier.onrender.com.",
        )
    if parsed.query or parsed.fragment:
        raise GameError("configuration", "Serveradressen kan ikke inneholde en query eller et fragment.")
    return url.rstrip("/")


class GameClient:
    def __init__(self, base_url: str, token: str = "", *, transport=None):
        self.base_url = validate_url(base_url)
        self.token = token
        self.transport = transport

    @classmethod
    def from_config(cls, path: Path = CONFIG_PATH):
        """Miljøvariablene ORBITAL_URL og ORBITAL_TOKEN overstyrer den lokale fila."""
        try:
            saved = json.loads(path.read_text()) if path.exists() else {}
            if not isinstance(saved, dict):
                raise ValueError("oppsettet må være et objekt")
        except (OSError, ValueError):
            raise GameError(
                "configuration",
                "Kan ikke lese spilleroppsettet.",
                "Kjør uv run python -m verktoy.oppsett for å rette opp oppsettet.",
            ) from None
        url = os.environ.get("ORBITAL_URL") or saved.get("url")
        token = os.environ.get("ORBITAL_TOKEN") or saved.get("token")
        if not isinstance(url, str) or not isinstance(token, str) or not url or not token:
            raise GameError(
                "configuration",
                "Spilleroppsett mangler.",
                "Kjør uv run python -m verktoy.oppsett først.",
            )
        return cls(url, token)

    def _request(self, method, path, *, body=None, params=None, timeout=5.0):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        if method == "POST" and path != "/api/join":
            headers["Idempotency-Key"] = str(uuid.uuid4())
        # Et nytt forsøk bruker samme nøkkel. Registrering gjentas aldri automatisk.
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
                            "Sjekk hele serveradressen og nettforbindelsen i miljøet du kjører fra."
                        )
                        if path == "/api/join":
                            hint += (
                                " Registreringen kan ha nådd serveren. Be instruktøren"
                                " sjekke navnet ditt og gi deg et nytt token før du prøver igjen."
                            )
                        elif path == "/health":
                            hint += " Ingen registrering er sendt. Du kan kjøre oppsettet på nytt."
                        else:
                            hint += " Sjekk status før du gjentar en handling."
                        hint += "\n" + connection_detail(exc)
                        timed_out = isinstance(exc, httpx.TimeoutException)
                        raise GameError(
                            "timeout" if timed_out else "connection",
                            "Spillserveren svarte ikke innen tidsfristen."
                            if timed_out else "Kunne ikke koble til spillserveren.",
                            hint,
                        ) from None
        try:
            data = response.json()
        except ValueError:
            raise GameError(
                "invalid_response",
                "Serveren ga et uventet svar.",
                "Sjekk serveradressen eller spør instruktøren.",
                response.status_code,
            ) from None
        if not response.is_success:
            error = data.get("error", {}) if isinstance(data, dict) else {}
            raise GameError(
                error.get("code", "http_error"),
                error.get("message", "Forespørselen feilet."),
                error.get("hint", "Spør instruktøren om hjelp."),
                response.status_code,
            )
        if not isinstance(data, dict):
            raise GameError("invalid_response", "Forventet et JSON-objekt fra serveren.")
        return data

    def get(self, path: str, **params):
        """Gjør et GET-kall. Bruk helst spillfunksjonene under fra CLI-et ditt."""
        return self._request("GET", path, params=params)

    def post(self, path: str, **body):
        """Gjør et POST-kall med samme forespørselsnøkkel ved gjentatte forsøk."""
        return self._request("POST", path, body=body)

    def put(self, path: str, **body):
        return self._request("PUT", path, body=body)

    def join(self, name: str, join_code: str):
        return self._request(
            "POST", "/api/join", body={"name": name, "join_code": join_code}, timeout=30.0
        )

    def wait_until_ready(self):
        """Sjekk serveren med et lesekall før vi sender en registrering."""
        data = self._request("GET", "/health", timeout=httpx.Timeout(120.0, connect=15.0))
        if data.get("status") != "ok":
            raise GameError(
                "unavailable", "Spillserveren er ikke klar.",
                "Ingen registrering er sendt. Sjekk serveradressen eller spør instruktøren.",
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
