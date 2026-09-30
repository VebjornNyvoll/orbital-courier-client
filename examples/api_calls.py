"""Infrastructure examples, not a finished CLI. No requests run on import."""

from game_api import GameClient


def inspect(api: GameClient):
    return api.status(), api.list_contracts(status="open")


def load_two_food(api: GameClient):
    """A write example. Call only while practicing: this moves and loads your ship."""
    api.travel("earth")
    return api.load_cargo("food", quantity=2)


def rename(api: GameClient, name: str):
    """A PUT example. Names can change only during practice."""
    return api.rename(name)
