"""Command-line interface for brief evaluation."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from brief_evaluator.config import YamlCriteriaProvider
from brief_evaluator.pipeline import EvaluationPipeline
# from brief_evaluator.llm.openrouter import OpenRouterLLMClient
from brief_evaluator.extractor.stub import RegexBriefExtractor
from brief_evaluator.evaluator.stub import LLMBriefEvaluator
from brief_evaluator.question_generator.stub import LLMQuestionGenerator
from brief_evaluator.mvp_suggester.stub import LLMMVPSuggester
from brief_evaluator.response_writer.stub import LLMResponseWriter
from brief_evaluator.llm.ollama import OllamaLLMClient


def build_default_pipeline(criteria_path: Path | None = None) -> EvaluationPipeline:
    from brief_evaluator.llm.ollama import OllamaLLMClient
    # Можно указать любую модель из списка: tinyllama, phi3, mistral, llama3
    llm = OllamaLLMClient(model="llama3") # или "llama3", "phi3", "tinyllama"
    provider = YamlCriteriaProvider(criteria_path) if criteria_path else YamlCriteriaProvider()
    return EvaluationPipeline(
        extractor = RegexBriefExtractor(),
        evaluator=LLMBriefEvaluator(llm),
        question_generator=LLMQuestionGenerator(llm),
        mvp_suggester=LLMMVPSuggester(llm),
        response_writer=LLMResponseWriter(llm),
        criteria_provider=provider,
    )


@click.group()
@click.version_option(package_name="brief_evaluator")
def main() -> None:
    """AI-ассистент для оценки брифов на соответствие ТЗ."""


@main.command()
@click.option(
    "--brief",
    "brief_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Путь к файлу брифа",
)
@click.option(
    "--tz",
    "tz_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Путь к файлу технического задания (ТЗ)",
)
@click.option(
    "--criteria",
    "criteria_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Путь к YAML-файлу критериев",
)
def evaluate(
    brief_path: Path | None,
    tz_path: Path | None,
    criteria_path: Path | None,
) -> None:
    """Оценить бриф на соответствие ТЗ."""
    pipeline = build_default_pipeline(criteria_path)

    if brief_path is not None:
        response = pipeline.run_from_files(brief_path, tz_path=tz_path)
    else:
        if sys.stdin.isatty():
            raise click.UsageError(
                "Укажите --brief или передайте текст брифа через stdin."
            )
        brief_text = sys.stdin.read().strip()
        if not brief_text:
            raise click.UsageError(
                "Укажите --brief или передайте текст брифа через stdin."
            )
        technical_spec = tz_path.read_text(encoding="utf-8") if tz_path else None
        response = pipeline.run(brief_text, technical_spec=technical_spec)

    click.echo(response.formatted_text)


if __name__ == "__main__":
    main()