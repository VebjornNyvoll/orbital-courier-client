# Designing a CLI people can use

Begin with a task someone needs to complete. Sketch the command and the result before writing its implementation. Decide which inputs are essential, what defaults are safe, and how someone will know whether the operation succeeded.

Typer handles much of the parsing and help generation. The choices below remain yours.

| Design question | Useful Typer mechanism | What you still decide |
|---|---|---|
| How does a new user discover the task? | Command docstring, `help`, `epilog`, `--help` | Names, a runnable example, purpose and consequences |
| Which input is required? | Type annotations, `Argument`, `Option` | Positional arguments versus named settings; units and defaults |
| How can mistakes fail early? | `Path` checks, numeric bounds, `Enum` | Valid business values and checks requiring current application state |
| What does another script receive? | Boolean options, `typer.echo` | A documented JSON schema or stable plain-text format |
| How does failure travel back to the caller? | `err=True`, `typer.Exit` | A useful diagnosis, next action and meaningful exit status |
| Can a destructive action be cancelled? | `typer.confirm`, `--yes` | Exactly what changes, when to ask, dry-run behaviour and noninteractive handling |
| Which configuration wins? | `envvar`, defaults, callbacks if needed | An explicit precedence rule, secret handling and any config-file format |
| Do actions belong in a group? | `Typer`, `@app.command`, `add_typer` | A vocabulary that matches tasks rather than internal module names |
| How do we know the interface works? | `typer.testing.CliRunner` | Tests of help, streams, exit codes and side effects |

## A first-use check

Ask a colleague to install the tool, find help and complete one real task using your documentation. Watch without explaining. A successful test means they can choose inputs, understand the result and recover from a mistake. Attractive help formatting alone does not establish that.

Write a short getting-started walkthrough with expected output. Keep detailed reference material separate. Examples should work from the documented directory, with supplied fixtures or clearly identified prerequisites. Never include credentials in examples.

## Output and failure

Choose useful labels and units for a person. For automation, provide a format with stable field names and types. Keep stdout for results and stderr for diagnostics or progress. Colour must not be the only way to distinguish an error; redirected data must stay usable.

Test success, missing input, invalid input and an expected runtime failure. Zero means success. Document any distinction between nonzero codes that a script should use. Do not catch an error and then accidentally return success.

## Safety and responsiveness

Default to operations that preserve existing data. Describe the exact consequence before confirmation, and decline by default. Give unattended callers an explicit way to confirm; if interactive input is unavailable, fail clearly instead of hanging. A `--dry-run` must avoid the writes it claims to preview.

Use bounded network waits. For long work, show progress on stderr only when appropriate for the terminal, and make Ctrl+C responsive. A lost reply can leave an action's outcome uncertain; repeated writes need an intentional retry policy.

## Sharing and maintaining the tool

Package the app with a stable executable name once others depend on it. A `[project.scripts]` entry refers to an importable callable in an installed package; the entry alone is not a complete package. Provide a version, supported Python versions, installation instructions and an issue/support link.

Keep names and defaults consistent across commands. Renaming a flag, changing JSON fields or repurposing an exit code can break another person's workflow. Explain intentional changes and provide a migration path. Completion and short aliases are conveniences; they do not replace clear names and help.

## Further examples

- [Typer arguments and help](https://typer.tiangolo.com/tutorial/arguments/help/)
- [Paths](https://typer.tiangolo.com/tutorial/parameter-types/path/), [number bounds](https://typer.tiangolo.com/tutorial/parameter-types/number/) and [typed choices](https://typer.tiangolo.com/tutorial/parameter-types/enum/)
- [Prompts](https://typer.tiangolo.com/tutorial/prompt/) and [environment variables](https://typer.tiangolo.com/tutorial/arguments/envvar/)
- [Command groups](https://typer.tiangolo.com/tutorial/subcommands/) and [testing](https://typer.tiangolo.com/tutorial/testing/)
- [Packaging](https://typer.tiangolo.com/tutorial/package/), [version options](https://typer.tiangolo.com/tutorial/options/version/) and [completion](https://typer.tiangolo.com/tutorial/options-autocompletion/)
- [Command Line Interface Guidelines](https://clig.dev/) for wider design tradeoffs
