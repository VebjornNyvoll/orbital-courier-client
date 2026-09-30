# Making a CLI with Typer

We’ll turn a small Python function into a command that someone else can use from a terminal. It reads a CSV file, counts its data rows and shows its column names. The file-reading code is already in `tutorial/report_data.py`. We’ll work on how the user supplies input, finds help and understands the result.

You need Python functions and basic type annotations. We’ll explain Typer, `Annotated` and command decorators as they appear. You don’t need a game account or a running server for this part.

Each step changes a little code and gives you something to run. Some steps deliberately break the program. Make a prediction before running those commands, then compare it with what actually happens. The answers are below each experiment.

## Setup

From the client repository root:

```sh
uv sync --frozen
cd tutorial
uv run python main.py
```

You should see:

```text
Rows: 3
Columns: id, title, status
```

`uv sync` installs the project’s locked dependencies. `uv run` uses that environment. Keep your terminal in `tutorial` for the rest of the lesson and edit `main.py`.

If you lose your place, copy the **contents** of a checkpoint into `tutorial/main.py`. Keep the supplied `report_data.py` alongside it. The checkpoints are recovery points, not files to run from their own directory. [Starting file](../tutorial/checkpoints/00_start.py).

## 1. A Python function becomes a command

The starter calls `summarize` with a fixed path. To accept a path from the terminal, add `import typer`, change `print` to `typer.echo`, and replace the final call with `typer.run(summarize)`:

```python
from pathlib import Path

import typer
from report_data import summarize_csv


def summarize(source: Path):
    report = summarize_csv(source)
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    typer.run(summarize)
```

There are two different function calls here. `summarize_csv(source)` does the file reading. `typer.run(summarize)` gives Typer a function to call after it has processed the command line. Notice that `summarize` has no parentheses in that last line. Calling it yourself would require supplying `source` yourself too.

Typer reads `source: Path` and makes it a required positional argument. It converts the incoming text into a `pathlib.Path` before calling the function. `typer.echo` prints the result to the output stream.

```sh
uv run python main.py data/tickets.csv
uv run python main.py --help
uv run python main.py
```

**Try it:** Which of these calls reaches the body of `summarize`? How can help work without a source file? If you’re unsure, temporarily add `typer.echo("summarize ran")` as the first line in the function, then repeat the commands. Remove that line afterwards.

<details markdown="1">
<summary>Explanation</summary>

Only the first call reaches the function. Typer produces help without running it. For the last call, it reports the missing argument before the function can run. This matters when your command talks to a service: displaying help should not require the service to be available. Code at module level still runs on import, so keep actual work inside the command function.

</details>

[Checkpoint 01](../tutorial/checkpoints/01_command.py).

## 2. Arguments, options and defaults

Suppose the file uses a different character encoding. A second positional argument could work, but the caller would have to remember what the second value means. A named `--encoding` option makes the command easier to read and lets us choose a default.

Change the signature and pass the value to the reader. Keep both output lines:

```python
def summarize(source: Path, encoding: str = "utf-8"):
    report = summarize_csv(source, encoding=encoding)
```

For ordinary parameters without explicit Typer metadata, a parameter with no default becomes a required argument, while a parameter with a default becomes an option. Both are parameters in Python. The distinction is how a user supplies them in the terminal.

```sh
uv run python main.py data/tickets.csv
uv run python main.py data/tickets.csv --encoding utf-8
uv run python main.py --help
```

Both reports should be the same. The second call supplies the value explicitly. The first uses the default, which should also appear in help.

**Try it:** Remove `= "utf-8"` from the signature. Look at help, then try `uv run python main.py data/tickets.csv utf-8`. Did encoding become a required option, or an argument? Restore the default afterwards.

<details markdown="1">
<summary>Explanation</summary>

It became a positional argument. Typer inferred that from the absence of a default. Later, `typer.Option` lets us specify that a parameter is an option explicitly, including when it has no default. “Argument” and “required” are different properties. A required `--input` option is a valid design too.

</details>

[Checkpoint 02](../tutorial/checkpoints/02_options.py).

## 3. Help that explains the command

The help page knows our parameter names and types. It doesn’t know why anyone would run the program. Add a docstring as the first statement inside `summarize`:

```python
    """Count data rows and show the column names in a CSV file.

    Example: uv run python main.py data/tickets.csv
    """
```

Run `--help` again. The docstring now explains the result and gives a first invocation. That is information Typer cannot work out from the type annotations.

We should also say what belongs in the file. Add `from typing import Annotated` and replace the two parameters with:

```python
source: Annotated[
    Path,
    typer.Argument(help="CSV file with a header row."),
],
encoding: Annotated[
    str,
    typer.Option(help="Character encoding of the CSV file."),
] = "utf-8",
```

These lines belong inside `def summarize(...)`. `Annotated` combines a type with metadata. `Path` is still the type of `source`. `typer.Argument(...)` adds information that Typer uses when building the command. It does not change the value your function receives.

For `encoding`, the default stays outside `Annotated`. We have made it explicit that this parameter is an option and added its description.

Look at help once more. Could someone identify the expected file format without reading your code? “Source file” would repeat the name but omit the header requirement.

[Checkpoint 03](../tutorial/checkpoints/03_help.py).

## 4. Validation before the function runs

`Path` converts text to a path object. It doesn’t, by itself, require the file to exist. Add these checks to the source parameter:

```python
source: Annotated[
    Path,
    typer.Argument(
        exists=True, dir_okay=False, readable=True,
        help="CSV file with a header row.",
    ),
],
```

Now try a missing path, a directory and a valid file:

```sh
uv run python main.py missing.csv
uv run python main.py data
uv run python main.py data/tickets.csv
```

The first two should fail before `summarize` runs. The third should still print the report. Read the actual error messages: do they identify what you need to correct?

**Try it:** Run `uv run python main.py data/broken.csv`. The file exists and is readable, but one record has too few fields. Why doesn’t the path declaration handle this failure too?

<details markdown="1">
<summary>Explanation</summary>

The path checks all pass. Typer calls our function, and `summarize_csv` then discovers the malformed contents and raises `SummaryError`. Typer knows about paths, but it cannot infer our CSV rules from that annotation. At this checkpoint, the error reaches the terminal as a traceback. We’ll handle that next.

</details>

[Checkpoint 04](../tutorial/checkpoints/04_validation.py). For other input types, Typer supports [numeric bounds](https://typer.tiangolo.com/tutorial/parameter-types/number/) and [choices through Enum](https://typer.tiangolo.com/tutorial/parameter-types/enum/).

## 5. Expected failures, error output and exit codes

Change the helper import to `from report_data import SummaryError, summarize_csv`. Replace the call to `summarize_csv` with:

```python
    try:
        report = summarize_csv(source, encoding=encoding)
    except SummaryError as exc:
        typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
        raise typer.Exit(1) from None
```

Keep the normal output below this block. Run the malformed-file command again. Instead of the traceback, you should see a message identifying the record and suggesting that you check its commas and quoting.

The handler catches a known failure from the reader. Catching every `Exception` would also catch programming bugs, which need investigation rather than a misleading explanation about the input.

There are two separate parts to reporting failure:

- `err=True` writes to **stderr**, the stream for errors and diagnostic messages. Normal results go to **stdout**.
- `raise typer.Exit(1)` stops execution with a nonzero **exit code**. Another program can check that code without understanding the error text.

Printing an error and returning normally would still report success to the calling process. Returning the integer `1` from the Python function does not set the process exit code either.

In Bash, check immediately after the failing command:

```sh
uv run python main.py data/broken.csv
echo $?
```

PowerShell uses `$LASTEXITCODE`. You should get `1`. Try the valid sample to get `0`, and a missing source argument to see Typer’s `2`. The general convention is zero for success and nonzero for failure. The meanings of particular nonzero codes depend on the tool.

[Checkpoint 05](../tutorial/checkpoints/05_errors.py).

## 6. Exercise: JSON output

The report is readable, but another program would need to pull the number out of `Rows: 3`. Add a `--json` flag so a caller can ask for structured output. Keep the readable output as the default.

Add `import json`. Use the Python parameter name `as_json` so you don’t hide the imported module. This declaration gives it the CLI name `--json`:

```python
as_json: Annotated[
    bool, typer.Option("--json", help="Print JSON for scripts."),
] = False,
```

Put it after the required source parameter. A Boolean flag does not need a value: `--json` means true. You don’t write `--json True`.

Write the output branch yourself, then check:

```sh
uv run python main.py data/tickets.csv
uv run python main.py data/tickets.csv --json
uv run python main.py --help
```

The entire stdout of the second command should be a JSON document. The existing error handler should still work in either mode.

<details markdown="1">
<summary>One solution</summary>

After reading the report and handling errors, replace the two output statements with:

```python
    if as_json:
        typer.echo(json.dumps(report))
        return
    typer.echo(f"Rows: {report['rows']}")
    typer.echo(f"Columns: {', '.join(report['columns'])}")
```

Without the `return`, execution would print the readable lines after the JSON. That is no longer a valid JSON document. An `if`/`else` would work too.

</details>

**Try it:** Temporarily remove that `return` and run this in your VM:

```sh
uv run python main.py data/tickets.csv --json | python -m json.tool
```

The pipe sends our stdout to another program. Python’s JSON parser should reject the extra text. Restore `return` and try again. This is why progress messages and banners must not share the result stream.

[Checkpoint 06](../tutorial/checkpoints/06_json.py).

## 7. Two commands in one tool

Suppose someone wants a list of column names with no report labels. We could add another mode flag, but `columns` is a distinct task. Giving it a command name makes it visible in top-level help.

Add `app = typer.Typer(no_args_is_help=True)` below the imports. Put `@app.command()` directly above your existing `def summarize(...)`. Keep its entire signature and body. Replace `typer.run(summarize)` at the bottom with `app()`.

The app holds the command registrations. The decorator tells it about the function. With two commands registered, Typer uses the first word after `main.py` to choose which one to call. A single decorated command normally stays flat, so finish adding the second function before testing the new command names.

Add this function above the final `if __name__ == "__main__":` block:

```python
@app.command()
def columns(
    source: Annotated[
        Path,
        typer.Argument(
            exists=True, dir_okay=False, readable=True,
            help="CSV file with a header row.",
        ),
    ],
    encoding: Annotated[
        str, typer.Option(help="Character encoding of the CSV file."),
    ] = "utf-8",
):
    """Print one column name per line."""
    try:
        report = summarize_csv(source, encoding=encoding)
    except SummaryError as exc:
        typer.echo(f"Error: {exc.message}\n{exc.hint}", err=True)
        raise typer.Exit(1) from None
    for name in report["columns"]:
        typer.echo(name)
```

The parameters and error handling deliberately match `summarize`. The output is the difference. Once you understand the two commands, you could extract their common code into a helper.

Update the example in `summarize`’s docstring to include its new command name. Then run:

```sh
uv run python main.py --help
uv run python main.py summarize --help
uv run python main.py summarize data/tickets.csv --json
uv run python main.py columns data/tickets.csv
```

**Try it:** Run the old invocation, `uv run python main.py data/tickets.csv`. Why does it fail now? Where does a new user find the correct invocation?

<details markdown="1">
<summary>Explanation</summary>

Typer now expects a command name first, so it interprets the path as an unknown command. The top-level help lists the operations. Per-command help explains their inputs. This is an interface change. For a tool that others already use, consider compatibility and update examples before releasing it.

</details>

[Checkpoint 07](../tutorial/checkpoints/07_commands.py).

## 8. Configuration and tests

If users repeatedly choose an encoding, an environment variable can save typing. Add `envvar="REPORT_ENCODING"` to `typer.Option(...)` for encoding in **both** commands. The order is explicit option, then environment variable, then the Python default.

In Bash:

```sh
export REPORT_ENCODING=does-not-exist
uv run python main.py summarize data/tickets.csv
uv run python main.py summarize data/tickets.csv --encoding utf-8
unset REPORT_ENCODING
```

In PowerShell:

```powershell
$env:REPORT_ENCODING = "does-not-exist"
uv run python main.py summarize data/tickets.csv
uv run python main.py summarize data/tickets.csv --encoding utf-8
Remove-Item Env:REPORT_ENCODING
```

The first call fails because the encoding is unknown. The explicit option overrides it and succeeds. Clear the environment variable afterwards and check how help documents it. Typer does not automatically read configuration files. You would have to define that format and where it fits in the precedence order.

[Checkpoint 08](../tutorial/checkpoints/08_configuration.py).

We have tried many commands manually. `CliRunner` can automate those checks:

```python
import json
from typer.testing import CliRunner
from main import app

result = CliRunner().invoke(app, [
    "summarize", "data/tickets.csv", "--json",
])
assert result.exit_code == 0
assert json.loads(result.stdout)["rows"] == 3
assert result.stderr == ""
```

That example assumes the working directory is `tutorial`. Tests in the repository resolve their sample paths explicitly so they also run from the root. Use `cd ..`, then `uv run pytest -q tests/test_tutorial.py` to run them. Look for tests of failures and help, not just successful output. Calling the underlying Python function directly would skip Typer’s argument handling.

## Before sharing your own tool

The CSV tool does not change files. For tools that write or delete things, decide how to preserve existing work, when to confirm an action and how to behave in a script with no one available to answer a prompt. `tutorial/safety_example.py` shows a confirmation guard. Its tests verify that a refusal stops before a write.

For longer operations, show progress on stderr, set network timeouts and make cancellation work. Installation and a first successful invocation belong in your README. A version command helps when someone reports a problem. [Typer’s packaging guide](https://typer.tiangolo.com/tutorial/package/) explains how an installable package can expose a short command name.

Use the [CLI design guide](cli-design.md) as a reference. Then open [the game exercise](exercises.md) and apply these ideas to a different program. The point of that exercise is to make the interface decisions yourself.

## Sources

The lesson’s small edits, explicit explanations and deliberate-break experiments take inspiration from [Imre Kerr’s FastAPI workshop](https://github.com/imre-kerr-sb1/fastapi-workshop/tree/main/docs). The examples here are specific to Typer. For the library behaviour, see the [Typer tutorial](https://typer.tiangolo.com/tutorial/). The [Command Line Interface Guidelines](https://clig.dev/) cover the wider design decisions.
