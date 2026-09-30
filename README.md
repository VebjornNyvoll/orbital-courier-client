# Orbital Courier: build a great Python CLI

A hands-on Typer workshop for people who already write Python. You will design a CLI for a small delivery game. The supplied `game_api.py` handles HTTP, configuration, and network failures.

## Before the workshop

Install **Python 3.12+**, **Git**, and [uv](https://docs.astral.sh/uv/getting-started/installation/). An editor and terminal are enough. Run the following on Windows PowerShell, macOS, or Linux:

```sh
git clone https://github.com/VebjornNyvoll/orbital-courier-client.git
cd orbital-courier-client
uv sync --frozen
uv run python tutorial/main.py Alex
uv run python tutorial/main.py --help
uv run pytest -q
```

The repository is private initially. Your instructor must give you access before cloning, or provide a ZIP. For a ZIP, extract it and start at `uv sync --frozen`.

## Part 1: your first Typer CLI

Edit `tutorial/main.py` as the instructor explains arguments, options, help, validation, and commands. This exercise needs no game server. [Follow-along checkpoints](docs/tutorial.md) tell you what to try after each step.

## Part 2: your courier CLI

Your instructor supplies the server URL and workshop join code. Register once:

```sh
uv run python setup_player.py
uv run python cli.py --help
uv run python cli.py status
```

Setup saves `.player.json` in this checkout. Do not share it or commit it. If a registration response is lost, ask the instructor to recover your token instead of registering a second identity. Your token can also be used in the server's `/docs` page under **Authorize**. Paste only the token, without the word `Bearer`.

Work primarily in `cli.py`. See [the exercises](docs/exercises.md), [game rules](docs/game-rules.md), and [API guide](docs/api-guide.md). Write your usage examples in `USAGE.md`. Additional Python command modules may live in `commands/`. Use the dependencies already provided so everyone can run your CLI consistently.

## Your target

Someone should be able to find a contract, inspect its requirements, load cargo, and make a delivery using only your help text and usage guide. They should also understand how to recover from a mistake.

Useful checks:

```sh
uv run pytest -q
uv run ruff check .
uv run python cli.py status --json
uv run python export_submission.py
```

The last command creates `submission.zip` containing only `cli.py`, `USAGE.md`, and optional `commands/*.py` files. It excludes the supplied infrastructure and your saved credentials.

## Configuration and troubleshooting

- Configuration precedence: `ORBITAL_URL` / `ORBITAL_TOKEN` environment variables, then `.player.json`. Environment variables override each field separately.
- No configuration? Run `setup_player.py`. Keep API calls inside command functions so help works without configuration.
- Connection failure? Check the URL with the instructor and open `<server>/health` in a browser. `localhost` means your own computer.
- Cargo full? Deliver it or unload it. Capacity is six units across all items.
- Invalid token? Ask the instructor for recovery and rerun setup, selecting an existing token.
- `--help` output is available offline. Shell completion is optional and shell-dependent.

## Further reading

[CLI Guidelines](https://clig.dev/) · [Typer tutorial](https://typer.tiangolo.com/tutorial/) · [Typer testing](https://typer.tiangolo.com/tutorial/testing/)

