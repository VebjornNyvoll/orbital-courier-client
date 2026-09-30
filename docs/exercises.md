# Build your CLI

## Milestone 1: discovery (20 minutes)

Add commands to list stations and open contracts. Give commands short descriptions. Make a contract ID easy to find and inspect. Verify every help page without a running server.

Done when: another person can identify the cargo, quantity, source, and destination for one delivery without reading Python.

## Milestone 2: a complete delivery (30 minutes)

Add travel, loading, and delivery commands. Use an argument for the thing being acted on and options for modifiers where that makes sense. Validate quantities before sending the request. Handle `GameError` with stderr and a nonzero exit code.

Done when: one contract can be completed entirely through your CLI, and an invalid quantity produces a useful error.

## Milestone 3: recovery and documentation (20 minutes)

Add unloading and practice reset. Confirm before reset; optionally accept `--yes` for scripts. A noninteractive invocation should fail with instructions instead of waiting for input. Describe capacity and practice-only restrictions. Fill in `USAGE.md` with current examples.

Done when: someone can recover from filling their ship with the wrong item and can cancel a reset safely.

## Milestone 4: usability rehearsal (20 minutes)

Try these without inspecting your code: find help, complete a delivery, correct a typo, handle full cargo, and recover from a server connection failure. Improve the weakest interaction.

Run `uv run python export_submission.py` when asked by the instructor.

## Extensions for faster participants

- Group commands such as `contracts list` and `contracts show`.
- Add `--json` while keeping stdout valid JSON and errors on stderr.
- Filter contracts and show useful cargo tables with Rich.
- Add a test for invalid input, cancellation, or a failing API operation using `CliRunner` and a fake API.
- Add explicit configuration options with documented precedence over environment and saved settings.
- Add a progress indicator on stderr, disabled for noninteractive output.
- Explore shell completion and a packaged command entry point after the core CLI works.

Avoid an automatic solver: this exercise measures how clearly a human can operate your commands.

