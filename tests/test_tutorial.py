"""Check the behaviours learners rely on as the example grows."""

import importlib.util
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

CHECKPOINTS = Path(__file__).resolve().parents[1] / "tutorial" / "checkpoints"


def load_app(checkpoint):
    spec = importlib.util.spec_from_file_location("lesson", CHECKPOINTS / f"{checkpoint}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "app"):
        return module.app
    app = typer.Typer()
    app.command()(module.label)
    return app


def test_first_argument_and_missing_input():
    app = load_app("01_argument")
    assert CliRunner().invoke(app, ["water"]).stdout == "Cargo: water\n"
    missing = CliRunner().invoke(app, [])
    assert missing.exit_code == 2
    assert "Missing argument" in missing.output
    assert "Cargo:" not in missing.stdout


def test_quantity_default_and_flag():
    app = load_app("03_flag")
    assert CliRunner().invoke(app, ["food"]).stdout == "Cargo: food\nUnits: 1\n"
    changed = CliRunner().invoke(app, ["food", "--quantity", "2", "--uppercase"])
    assert changed.exit_code == 0
    assert changed.stdout == "Cargo: FOOD\nUnits: 2\n"


@pytest.mark.parametrize("value", ["0", "7", "two"])
def test_invalid_quantity_never_prints_a_label(value):
    result = CliRunner().invoke(load_app("05_validation"), ["food", "--quantity", value])
    assert result.exit_code == 2
    assert "--quantity" in result.output
    assert "Cargo:" not in result.stdout


def test_command_group_and_both_help_levels():
    app = load_app("06_commands")
    runner = CliRunner()
    top = runner.invoke(app, ["--help"])
    assert top.exit_code == 0
    assert "label" in top.stdout and "items" in top.stdout
    detail = runner.invoke(app, ["label", "--help"])
    assert detail.exit_code == 0
    # Rich can wrap the description inside its help table on narrow terminals.
    assert "Number of cargo" in detail.stdout and "units." in detail.stdout
    assert "label food --quantity 2" in detail.stdout
    assert runner.invoke(app, ["label", "water", "--quantity", "3"]).stdout == (
        "Cargo: water\nUnits: 3\n"
    )
    assert runner.invoke(app, ["water"]).exit_code == 2
    assert "medicine" in runner.invoke(app, ["items"]).stdout
