# CLI patterns to use during the build

Use these when the basic delivery flow works or when you need a particular feature. They are not extra steps everyone must finish in the first lesson. The [Typer tutorial](https://typer.tiangolo.com/tutorial/) has complete examples.

## Expected failures and exit codes

Copy the pattern already used by `status` in `cli.py`. Both `GameClient.from_config()` and the network call belong inside the `try` block. Configuration can fail before a request.

```python
try:
    state = GameClient.from_config().status()
except GameError as exc:
    typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
    raise typer.Exit(1) from None
```

Results go to stdout. Diagnostics go to stderr. A successful command exits with zero; expected failures use a nonzero code. Avoid dumping a traceback for an ordinary full-cargo or network error. [Typer termination](https://typer.tiangolo.com/tutorial/terminating/).

## JSON output

The starter's `status --json` shows this pattern. The Python parameter is `as_json`, while the explicit terminal name is `--json`:

```python
as_json: Annotated[
    bool, typer.Option("--json", help="Print JSON for scripts.")
] = False
```

After obtaining `state`, print either `json.dumps(state)` or human-readable output. Do not print a heading, success message or progress bar on stdout in JSON mode. Test by passing `result.stdout` to `json.loads`. [CLI output guidance](https://clig.dev/#output).

## Confirming a practice reset

Explain what resets: location, cargo, completed contracts and practice points. Identity stays registered. This fragment assumes a `yes: bool = False` option and imports of `sys` and `typer`:

```python
if not yes:
    if not sys.stdin.isatty():
        typer.echo("Pass --yes to confirm the reset.", err=True)
        raise typer.Exit(2)
    if not typer.confirm("Erase your practice progress?", err=True):
        raise typer.Exit(0)
# Call game.reset_practice() inside the usual GameError handler.
```

Try declining and accepting. Declining must leave state unchanged. A redirected command should never wait indefinitely for input. [Typer prompts](https://typer.tiangolo.com/tutorial/prompt/).

## Restricting station names

An Enum lets Typer list valid choices and catch spelling errors before a request:

```python
from enum import Enum

class Station(str, Enum):
    earth = "earth"
    luna = "luna"
    mars = "mars"
    europa = "europa"
    titan = "titan"
```

Use `destination: Station` in the command and pass `destination.value` to `game.travel`. A string argument also works; the server validates it. Use an Enum when showing the choices locally improves help. [Typer choices](https://typer.tiangolo.com/tutorial/parameter-types/enum/).

## Command groups

A flat CLI is enough for this exercise. If several actions belong together, register a sub-app:

```python
contracts_app = typer.Typer(help="Find delivery contracts.")
app.add_typer(contracts_app, name="contracts")

@contracts_app.command("list")
def list_contracts():
    # Call the wrapper and format the result here.
    ...
```

The path becomes `python cli.py contracts list`. Document both `contracts --help` and `contracts list --help`. Avoid keeping a flat command with the same `contracts` name. [Typer subcommands](https://typer.tiangolo.com/tutorial/subcommands/).

## Testing the interface

Read `tests/test_cli.py`: it invokes commands with `CliRunner` and supplies a fake API. Test behaviours users depend on: help works without credentials, bad input makes no request, failures use stderr, cancellation leaves state unchanged, and JSON parses.

The tests in `tests/test_tutorial.py` also check the change from a single command to `label` and `items`. Run them with `uv run pytest -q tests/test_tutorial.py`. [Typer testing](https://typer.tiangolo.com/tutorial/testing/).

## More to explore after the workshop

Completion, packaged command names, aliases and progress indicators each add behaviour to document and test. Keep redirected output plain, send progress to stderr and make Ctrl+C responsive. Use the configuration precedence documented in the README; never include tokens in examples or submissions. For broader decisions, use [Command Line Interface Guidelines](https://clig.dev/).
