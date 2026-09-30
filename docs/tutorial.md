# Design a good CLI with Typer

The lesson uses a small CSV inspection tool. The supplied `tutorial/report_data.py` already counts records and reads column names. Your job is to design the interface: how someone discovers it, supplies input, reads a result and recovers from a mistake. The tool never changes the input file and needs no server.

Read the [CLI design guide](cli-design.md) alongside these steps. Each edit should answer a user need, not simply add another Typer feature.

## Setup and checkpoints

From the client repository root, run `cd tutorial`. Keep that terminal open and edit `main.py`. Run `uv run python main.py`: the starting program prints three rows and the column names from a fixed sample file.

If you lose your place, copy a checkpoint's **contents into `tutorial/main.py`**. The checkpoints depend on the supplied `report_data.py` beside that file; do not move the helper. Keep editing `main.py`, not the checkpoint. [Starting file](../tutorial/checkpoints/00_start.py).

Examples named `csvreport` in the slides are sketches of an installed interface. During this lesson, use `uv run python main.py` instead. No `csvreport` executable is installed by this repository.

## 1. Let the user choose the input

Import Typer, replace `print` with `typer.echo`, and replace the fixed call at the bottom with `typer.run(summarize)`. Pass the function without parentheses. Retain the supplied helper import and both output lines.

```sh
uv run python main.py data/tickets.csv
uv run python main.py --help
uv run python main.py
```

Predict which call reads a file, which describes the command and which reports missing input. `source: Path` becomes a required argument. A help request must not do the actual work. [Checkpoint 01](../tutorial/checkpoints/01_command.py).

Before adding options, discuss the proposed interface: why is the source positional, while `--encoding utf-8` and `--json` are named? What should happen when those settings are absent?

## 2. Write help someone can act on

Use a function docstring to explain the result and show a runnable example. Import `Annotated` and replace the source parameter with:

```python
source: Annotated[
    Path, typer.Argument(help="CSV file with a header row.")
],
```

This belongs inside `def summarize(...)`. Run `--help` and find the purpose, input description and example. A description such as “source file” would not explain the header requirement. [Checkpoint 02](../tutorial/checkpoints/02_help.py).

## 3. Reject bad paths before doing work

Add `exists=True, dir_okay=False, readable=True` to the `typer.Argument(...)` declaration. Typer can now reject a missing path or a directory before calling your function.

```sh
uv run python main.py missing.csv
uv run python main.py data
uv run python main.py data/tickets.csv
```

The first two calls should fail and the third should still work. Explain what a user should do after each error. A valid path does not guarantee valid CSV content; that is the next check. [Checkpoint 03](../tutorial/checkpoints/03_validation.py).

## 4. Make failures useful to people and scripts

Import `SummaryError` from `report_data`. Put the call to `summarize_csv` inside a `try`, catch that expected error, print its message and hint with `typer.echo(..., err=True)`, and stop with `raise typer.Exit(1) from None`.

Keep normal output below the handler. Try `uv run python main.py data/broken.csv`. The error identifies the malformed record and suggests checking commas and quoting. It should produce no successful result on stdout. Avoid catching every `Exception`: an unexpected programming bug needs investigation. [Checkpoint 04](../tutorial/checkpoints/04_errors.py).

## 5. Exercise: add JSON output

Keep the readable default. Add a Boolean option named `--json` with help explaining that it prints JSON for scripts. Use the Python name `as_json` and import `json`.

```python
as_json: Annotated[
    bool, typer.Option("--json", help="Print JSON for scripts.")
] = False,
```

Print `json.dumps(report)` when it is set and avoid falling through to the readable output. A flag does not take the word `True` after it.

```sh
uv run python main.py data/tickets.csv
uv run python main.py data/tickets.csv --json
```

Check both forms and the help page. The entire stdout of the second call must parse as JSON. There must be no banner, progress message or “Done!” mixed into it. Compare with [checkpoint 05](../tutorial/checkpoints/05_json.py) after your attempt.

Check exit status immediately after each command: `$LASTEXITCODE` in PowerShell, or `echo $?` in Bash/zsh. For this tool a successful result exits 0, invalid CLI input exits 2, and a file-processing failure exits 1. Other tools may choose different nonzero codes.

## 6. Keep configuration predictable

Add an `encoding` string option with default `"utf-8"`, help text and `envvar="REPORT_ENCODING"`. Pass `encoding=encoding` to the helper. The rule is explicit option, then environment variable, then default. [Checkpoint 06](../tutorial/checkpoints/06_configuration.py).

In PowerShell:

```powershell
$env:REPORT_ENCODING = "does-not-exist"
uv run python main.py data/tickets.csv
uv run python main.py data/tickets.csv --encoding utf-8
Remove-Item Env:REPORT_ENCODING
```

In Bash/zsh:

```sh
export REPORT_ENCODING=does-not-exist
uv run python main.py data/tickets.csv
uv run python main.py data/tickets.csv --encoding utf-8
unset REPORT_ENCODING
```

The first call should fail; the explicit option should succeed. Clean up the variable afterwards. Help should show both the environment variable and default. Typer does not automatically supply a configuration-file format or precedence policy.

## 7. Add commands when there are distinct tasks

Create `app = typer.Typer(no_args_is_help=True)`. Put `@app.command()` above the existing summarize function. Add the columns function from [checkpoint 07](../tutorial/checkpoints/07_commands.py), which prints one name per line and keeps the same path, encoding and error behaviour. Replace `typer.run(summarize)` with `app()`.

```sh
uv run python main.py --help
uv run python main.py summarize --help
uv run python main.py summarize data/tickets.csv --json
uv run python main.py columns data/tickets.csv
```

The command name is now required before the source. The old flat invocation no longer works. This is an interface change that would need care if others already used the tool. Nested command groups are optional; two tasks do not need a deep hierarchy.

## 8. Verify the interface

Return to the repository root with `cd ..`, then run `uv run pytest -q tests/test_tutorial.py`. Inspect tests for readable output, clean JSON, help without file access, invalid paths, useful errors and configuration precedence.

The lesson also discusses safe writes, prompts, progress, cancellation, installation and compatibility. These are design topics beyond the read-only CSV tool. `tutorial/safety_example.py` provides a confirmation guard, tested to stop before a write when confirmation is declined or unavailable. It is a reference, not a request to add file writes to this tool.

## Apply the principles

Give someone a task and your help text. Let them try without a verbal walkthrough. Note where they hesitate and improve that interaction.

Then open [the courier exercise](exercises.md). The game is a separate application of the same design decisions. The [game CLI patterns](cli-patterns.md) are available when you need confirmations, choices, JSON or groups during that build.
