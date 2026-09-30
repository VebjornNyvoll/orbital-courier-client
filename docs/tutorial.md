# Part 1 follow-along checkpoints

Start in `tutorial/main.py`. The instructor's examples use this file until the game exercise begins.

1. **Function to command.** Run `uv run python tutorial/main.py Alex`, then `--help`. A required `str` becomes a positional argument.
2. **Named options.** Add `formal: bool = False`. Try `Alex --formal`. Explain that a Python default normally creates a CLI option.
3. **Help with Annotated.** Import `Annotated` from `typing`. Write `name: Annotated[str, typer.Argument(help="Courier name.")]`. Add an explicit option with help.
4. **Validation.** Add `count: Annotated[int, typer.Option(min=1, max=5, help="Number of greetings.")] = 1`. Try `--count 0` and `--count banana`.
5. **Several commands.** Replace `typer.run(hello)` with `app = typer.Typer(...)`, decorate functions with `@app.command()`, and call `app()`. Add a callback so even one registered command keeps its explicit command name.
6. **Command groups.** Discuss `add_typer` and `contracts list`. Keep this optional if the group needs more practice with single commands.
7. **Failures.** Raise `typer.Exit(1)` after printing an expected failure with `err=True`. A successful command exits with zero.
8. **Confirmation.** Use `typer.confirm` for a destructive operation, and design a noninteractive path.
9. **Testing.** Read `tests/test_cli.py`. Notice that tests invoke the CLI and inject a fake API rather than needing the instructor server.

Checkpoint commands after converting to a multi-command app:

```sh
uv run python tutorial/main.py --help
uv run python tutorial/main.py hello --help
uv run python tutorial/main.py hello Alex --count 2
```

