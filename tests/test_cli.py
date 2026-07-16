"""CLI smoke tests."""

from pathlib import Path

from click.testing import CliRunner

from brief_evaluator.cli import main


def test_cli_evaluate_with_files(tmp_path: Path) -> None:
    runner = CliRunner()
    brief = tmp_path / "brief.txt"
    tz = tmp_path / "tz.txt"
    brief.write_text("Тестовый бриф\nОписание.", encoding="utf-8")
    tz.write_text("Техническое задание\nТребования.", encoding="utf-8")

    result = runner.invoke(
        main,
        ["evaluate", "--brief", str(brief), "--tz", str(tz)],
    )

    assert result.exit_code == 0
    assert "Оценка брифа" in result.output


def test_cli_evaluate_stdin(tmp_path: Path) -> None:
    runner = CliRunner()
    tz = tmp_path / "tz.txt"
    tz.write_text("ТЗ", encoding="utf-8")

    result = runner.invoke(
        main,
        ["evaluate", "--tz", str(tz)],
        input="Бриф из stdin",
    )

    assert result.exit_code == 0
    assert "Оценка брифа" in result.output


def test_cli_missing_input_shows_error() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["evaluate"])
    assert result.exit_code != 0
