# Provided Python API

```python
from game_api import GameClient, GameError

game = GameClient.from_config()
state = game.status()
print(state["location"])
```

Every method returns a normal Python dictionary. These are synchronous functions. You do not need async code, an HTTP library, or a server installation.

| Function | Result | HTTP operation |
|---|---|---|
| `game.status()` | location, cargo, score, completed, name, mode, capacity, supplies_here, player_id | GET /api/me |
| `game.session()` | mode, seconds_remaining | GET /api/session |
| `game.map()` | stations, travel_rule | GET /api/map |
| `game.list_contracts(status="open")` | contracts list | GET /api/contracts |
| `game.get_contract("P01")` | one contract | GET /api/contracts/P01 |
| `game.travel("luna")` | updated player state | POST /api/travel |
| `game.load_cargo("food", quantity=2)` | updated player state | POST /api/cargo/load |
| `game.unload_cargo("food", quantity=1)` | updated player state | POST /api/cargo/unload |
| `game.deliver("P01")` | updated player state | POST /api/contracts/P01/deliver |
| `game.reset_practice()` | fresh player state | POST /api/practice/reset |
| `game.rename("Alex")` | name | PUT /api/me/profile |

Contract filter values are `all`, `open`, and `completed`. A practice contract looks like:

```json
{"id":"P01","item":"food","source":"earth","destination":"luna","quantity":2,"reward":10,"completed":false}
```

`game.list_contracts(status="open")` puts those objects in `data["contracts"]`. Loop over that list, not the outer dictionary.

`game.map()` has a similar structure: `data["stations"]` is a list of station dictionaries. The first two entries look like this (the full response also includes Mars, Europa and Titan):

```json
{
  "stations": [
    {"id": "earth", "name": "Earth", "supplies": ["food", "water"]},
    {"id": "luna", "name": "Luna", "supplies": ["tools"]}
  ],
  "travel_rule": "Any station is reachable directly. Travel is free."
}
```

The excerpt shows the fields used in the lesson; see the server's `/docs` for the full response. Join a station's `supplies` list with `", ".join(station["supplies"])` when formatting a line for a person.

## A write example

```python
# This changes your practice state. Call it only when you intend to load cargo.
game.travel("earth")
state = game.load_cargo("food", quantity=2)
```

## Expected failures

```python
try:
    state = game.load_cargo("food", quantity=2)
except GameError as exc:
    # Decide how your CLI should present the problem.
    # exc.code: stable error identifier, e.g. "cargo_full"
    # exc.message: what went wrong
    # exc.hint: how to recover
    # exc.status: HTTP status, or 0 for a local/network error
    ...
```

Common codes: `configuration`, `connection`, `unauthorized`, `cargo_full`, `missing_cargo`, `wrong_station`, `unavailable_cargo`, `already_delivered`, `practice_only`, `round_inactive`.

`get(path, **params)`, `post(path, **body)`, and `put(path, **body)` exist to illustrate the underlying HTTP operations. Prefer the named methods in your workshop CLI.

The wrapper uses five-second HTTP timeouts and at most one automatic transport retry. Mutating POST retries reuse a unique request key. Registration is never retried automatically. If both attempts fail, inspect your status before issuing a new command: a lost response does not prove that an action failed.

