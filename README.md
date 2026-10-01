# Kometfrakteratene: build a great Python CLI

Open [the styled workshop guide](docs/index.html) in a browser after cloning. It includes setup, the Typer tutorial, exercises and API guidance, and works offline.

A hands-on Typer workshop for people who already write Python. You will design a CLI for a small delivery game. The supplied `game_api.py` handles HTTP, configuration, and network failures.

## Before the workshop

Install **Python 3.12+**, **Git**, and [uv](https://docs.astral.sh/uv/getting-started/installation/). An editor and terminal are enough. Run the following on Windows PowerShell, macOS, or Linux:

If using a workshop cloud VM, run these commands in that VM's terminal and edit the checkout there. The game server is hosted separately; you do not need to install or start it.

```sh
git clone https://github.com/VebjornNyvoll/orbital-courier-client.git
cd orbital-courier-client
uv sync --frozen
uv run python tutorial/main.py
uv run pytest -q
```

The repository is private initially. Your instructor must give you access before cloning, or provide a ZIP. For a ZIP, extract it and start at `uv sync --frozen`.

## Part 1: your first Typer CLI

Learn how to design useful commands, then implement those choices with Typer. The follow-along example is a CSV inspection tool in `tutorial/main.py`, independent of the game. Its file-reading function and sample data are supplied. The [worksheet](docs/tutorial.md) connects help, validation, errors, output and configuration to a user's needs, with complete checkpoints if you lose your place. The starting file prints `Rows: 3` and the column names; command-line input and `--help` work after the first edit. Keep the [CLI design guide](docs/cli-design.md) as a reference for your own tools.

## Part 2: your courier CLI

After the lesson, apply the design principles to a different tool: a courier game CLI. Your instructor supplies the public HTTPS server URL and workshop join code. Register during the break before the build. Use the base URL without `/docs` or `/api`. Register once:

```sh
uv run python setup_player.py
uv run python cli.py --help
uv run python cli.py status
```

Setup saves `.player.json` in this checkout. Do not share it or commit it. If a registration response is lost, ask the instructor to recover your token instead of registering a second identity. Your token can also be used in the server's `/docs` page under **Authorize**. Paste only the token, without the word `Bearer`.

Work primarily in `cli.py`. Read the supplied `status` command as an example, then design your command interface before implementing the other actions. Follow [the exercises](docs/exercises.md), [game rules](docs/game-rules.md), and [API guide](docs/api-guide.md). The [game CLI patterns](docs/cli-patterns.md) cover confirmations, JSON, typed choices and tests when you need them. Write your usage examples in `USAGE.md`. Additional Python command modules may live in `commands/`. Use the dependencies already provided so everyone can run your CLI consistently.

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
- Connection failure? Check the URL with the instructor and open `<server>/health` in a browser. In a cloud VM, `localhost` means the VM itself. Use the instructor's public HTTPS URL; no incoming VM ports are needed.
- Setup defaults to `https://orbital-courier.onrender.com` (or `ORBITAL_URL` if set). It checks `/health` and waits up to two minutes for a sleeping host before asking for registration details. If registration itself times out, ask the instructor to check your display name and recover your token before registering again.
- Cargo full? Deliver it or unload it. Capacity is six units across all items.
- Invalid token? Ask the instructor for recovery and rerun setup, selecting an existing token.
- `--help` output is available offline. Shell completion is optional and shell-dependent.

## Further reading

[CLI Guidelines](https://clig.dev/) · [Typer tutorial](https://typer.tiangolo.com/tutorial/) · [Typer testing](https://typer.tiangolo.com/tutorial/testing/)

