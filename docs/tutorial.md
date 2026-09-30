# Part 1: a cargo-label CLI

Keep editing `tutorial/main.py` throughout this lesson. It starts as an ordinary Python function. This program prints labels; it never contacts the game server or changes your cargo.

Run commands from the repository root. If you lose your place, open the linked checkpoint and copy its contents into `tutorial/main.py`. Each checkpoint is a complete file. Use the checkpoint that matches your current step.

## 1. Run the starting file

```sh
uv run python tutorial/main.py
```

You should see `Cargo: food`. Find the line that supplies `"food"` to the function. We want to supply that value in the terminal instead. [Starting file](../tutorial/checkpoints/00_start.py).

## 2. Let Typer supply the argument

Import `typer`. Replace `print` with `typer.echo` and replace `label("food")` with `typer.run(label)`. Pass the function itself, without parentheses after `label`.

```sh
uv run python tutorial/main.py water
uv run python tutorial/main.py --help
uv run python tutorial/main.py
```

Predict each result before running it. `water` should print a label. `--help` should describe the required `ITEM`. The last call should fail because no item was supplied. [Checkpoint 01](../tutorial/checkpoints/01_argument.py).

## 3. Add a quantity option

Add `quantity: int = 1` to the function signature. Add `typer.echo(f"Units: {quantity}")` after the cargo line. Keep the import and entry point.

```sh
uv run python tutorial/main.py food
uv run python tutorial/main.py food --quantity 2
```

The first label has one unit. The second has two. `food` is a positional argument; `--quantity` is a named option. [Checkpoint 02](../tutorial/checkpoints/02_quantity.py).

## 4. Exercise: uppercase labels

Add an `--uppercase` flag without breaking quantity. Start with `uppercase: bool = False` in the signature. Use `item.upper()` only when the flag is set.

```sh
uv run python tutorial/main.py food --uppercase --quantity 2
```

Expected output:

```text
Cargo: FOOD
Units: 2
```

Run again without `--uppercase`: the name should stay lowercase. Do not put `True` after the flag. If finished early, inspect `--help` and try the negative form. Compare with [checkpoint 03](../tutorial/checkpoints/03_flag.py) after your attempt.

## 5. Add help to the option

Import `Annotated` from `typing`. Replace only the quantity parameter with:

```python
quantity: Annotated[
    int, typer.Option(help="Number of cargo units.")
] = 1,
```

This belongs inside `def label(...)`. Keep `item` and `uppercase`. Add a command description and an example to the function docstring, then run `--help`. Find both the description and the option's help text. [Checkpoint 04](../tutorial/checkpoints/04_help.py).

## 6. Reject quantities that cannot fit

Add `min=1, max=6` to the same `typer.Option(...)`. The integer type checks whether the input is a number; the range checks whether that number is allowed.

```sh
uv run python tutorial/main.py food --quantity 6
uv run python tutorial/main.py food --quantity 0
uv run python tutorial/main.py food --quantity two
```

Six should succeed. Zero and `two` should fail for different reasons, before a label is printed. Explain those reasons to the person beside you. [Checkpoint 05](../tutorial/checkpoints/05_validation.py).

## 7. Add a second command

Create `app = typer.Typer(no_args_is_help=True)` after the imports. Put `@app.command()` above the existing `label` function. Keep its parameters and body.

Add an `items` function below it, also decorated with `@app.command()`. Give it a docstring and print `food, water, tools, medicine, fuel, parts`. Finally, replace `typer.run(label)` with `app()`.

```sh
uv run python tutorial/main.py --help
uv run python tutorial/main.py items
uv run python tutorial/main.py label --help
uv run python tutorial/main.py label water --quantity 3
```

The `label` command name is now required before the item. Top-level help lists commands; `label --help` explains the inputs for label. [Checkpoint 06](../tutorial/checkpoints/06_commands.py).

## 8. Use the same structure in the game client

Open `cli.py`. It already has a Typer app and a `status` command. Keep that command and its imports. The instructor will add `map` with you, calling `GameClient.from_config().map()` and printing each station's ID and supplies.

Put new commands above the final `if __name__ == "__main__": app()` block. Keep API calls inside command functions so help stays available offline.

The completed map command, for reference after following the live edit:

```python
@app.command("map")
def show_map():
    """List stations and their supplies."""
    try:
        data = GameClient.from_config().map()
    except GameError as exc:
        typer.echo(exc.message, err=True)
        typer.echo(exc.hint, err=True)
        raise typer.Exit(1)
    for station in data["stations"]:
        supplies = ", ".join(station["supplies"])
        typer.echo(f"{station['id']}: {supplies}")
```

Run `uv run python cli.py map --help`, then `uv run python cli.py map`. You should see five stations and the cargo available at each.

Then add `contracts` yourself. Use the map command as your example. `game.list_contracts(status="open")` returns a dictionary with a `contracts` list. Each contract contains `id`, `item`, `quantity`, `source` and `destination`.

If you need a starting point, complete this fragment inside your command:

```python
game = GameClient.from_config()
data = game.list_contracts(status="open")
for contract in data["contracts"]:
    # Print the ID, amount, cargo, source and destination.
    ...
```

Keep configuration, the API call and the existing `GameError` handling together. The supplied [API guide](api-guide.md) describes the dictionaries. Your command should let someone choose a delivery without reading Python.

Continue with [the build exercise](exercises.md). Optional features are in [CLI patterns](cli-patterns.md).
