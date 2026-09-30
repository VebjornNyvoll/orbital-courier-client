"""Exercise the CLI contract taught in the CSV lesson."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from rich.text import Text
import typer
from typer.testing import CliRunner

TUTORIAL = Path(__file__).resolve().parents[1] / "tutorial"
sys.path.insert(0, str(TUTORIAL))
DATA = TUTORIAL / "data" / "tickets.csv"


def load_module(name, checkpoint=True):
    folder = TUTORIAL / "checkpoints" if checkpoint else TUTORIAL
    spec = importlib.util.spec_from_file_location(name, folder / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def app_for(module):
    if hasattr(module, "app"):
        return module.app
    app = typer.Typer()
    app.command()(module.summarize)
    return app


@pytest.mark.parametrize("checkpoint", [
    "01_command", "02_help", "03_validation", "04_errors", "05_json", "06_configuration",
])
def test_each_single_command_checkpoint_reads_the_sample(checkpoint):
    result = CliRunner().invoke(app_for(load_module(checkpoint)), [str(DATA)])
    assert result.exit_code == 0, result.exception
    assert result.stdout == "Rows: 3\nColumns: id, title, status\n"
    assert not result.stderr


def test_help_and_invalid_paths_never_read_the_file(monkeypatch, tmp_path):
    module = load_module("07_commands")

    def must_not_run(*args, **kwargs):
        raise AssertionError("Parsing and help must finish before reading a file")

    monkeypatch.setattr(module, "summarize_csv", must_not_run)
    for args in (["--help"], ["summarize", "--help"], ["columns", "--help"]):
        assert CliRunner().invoke(module.app, args).exit_code == 0
    for source in (tmp_path / "missing.csv", tmp_path):
        result = CliRunner().invoke(module.app, ["summarize", str(source)])
        assert result.exit_code == 2
        assert "Invalid value" in Text.from_ansi(result.output).plain


def test_json_and_columns_are_clean_results():
    app = load_module("07_commands").app
    result = CliRunner().invoke(app, ["summarize", str(DATA), "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"rows": 3, "columns": ["id", "title", "status"]}
    assert not result.stderr
    columns = CliRunner().invoke(app, ["columns", str(DATA)])
    assert columns.exit_code == 0
    assert columns.stdout == "id\ntitle\nstatus\n"
    assert CliRunner().invoke(app, [str(DATA)]).exit_code == 2


def test_malformed_csv_has_recovery_message_and_failure_exit():
    app = load_module("07_commands").app
    result = CliRunner().invoke(app, ["summarize", str(TUTORIAL / "data" / "broken.csv")])
    assert result.exit_code == 1
    assert not result.stdout
    assert "line 2 has 2 fields" in result.stderr
    assert "Check commas and quoting" in result.stderr
    assert "Traceback" not in result.stderr


def test_explicit_encoding_overrides_environment():
    app = load_module("07_commands").app
    env = {"REPORT_ENCODING": "does-not-exist"}
    failure = CliRunner().invoke(app, ["summarize", str(DATA)], env=env)
    assert failure.exit_code == 1
    override = CliRunner().invoke(
        app, ["summarize", str(DATA), "--encoding", "utf-8"], env=env,
    )
    assert override.exit_code == 0
    assert "Rows: 3" in override.stdout


@pytest.mark.parametrize("interactive", [False, True])
def test_overwrite_guard_stops_before_a_write(monkeypatch, tmp_path, interactive):
    safety = load_module("safety_example", checkpoint=False)
    output = tmp_path / "report.json"
    output.write_text("original")
    app = typer.Typer()

    @app.command()
    def export(yes: bool = False):
        safety.confirm_replace(output, yes)
        output.write_text("replacement")

    # CliRunner replaces stdin; inject only the guard's interactivity check.
    monkeypatch.setattr(safety, "sys", SimpleNamespace(
        stdin=SimpleNamespace(isatty=lambda: interactive),
    ))
    denied = CliRunner().invoke(app, [], input="n\n")
    assert denied.exit_code != 0
    assert output.read_text() == "original"
    accepted = CliRunner().invoke(app, ["--yes"])
    assert accepted.exit_code == 0
    assert output.read_text() == "replacement"
