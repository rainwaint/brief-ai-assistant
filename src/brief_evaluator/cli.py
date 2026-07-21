from __future__ import annotations

from pathlib import Path
import click

from brief_evaluator.config import YamlCriteriaProvider
from brief_evaluator.pipeline import EvaluationPipeline
from brief_evaluator.llm.yandex import YandexGPTClient  # <-- импорт
from brief_evaluator.extractor.stub import LLMBriefExtractor
from brief_evaluator.evaluator.stub import LLMBriefEvaluator
from brief_evaluator.question_generator.stub import LLMQuestionGenerator
from brief_evaluator.mvp_suggester.stub import LLMMVPSuggester
from brief_evaluator.response_writer.stub import LLMResponseWriter


def build_default_pipeline(criteria_path: Path | None = None) -> EvaluationPipeline:
    # Используем YandexGPT вместо Ollama
    llm = YandexGPTClient(model="yandexgpt-lite", timeout=60)
    provider = YamlCriteriaProvider(criteria_path) if criteria_path else YamlCriteriaProvider()

    return EvaluationPipeline(
        extractor=LLMBriefExtractor(llm),
        evaluator=LLMBriefEvaluator(llm),
        question_generator=LLMQuestionGenerator(llm),
        mvp_suggester=LLMMVPSuggester(llm),
        response_writer=LLMResponseWriter(llm),
        criteria_provider=provider,
    )


@click.group()
@click.version_option(package_name="brief_evaluator")
def main() -> None:
    """AI-ассистент для оценки брифов."""


@main.command()
@click.option("--brief", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Путь к файлу брифа")
@click.option("--save", is_flag=True, help="Сохранить результат в JSON")
def evaluate(brief: Path | None, save: bool) -> None:
    pipeline = build_default_pipeline()

    if brief is None:
        raise click.UsageError("Укажите --brief")
    
    response = pipeline.run_from_files(brief)
    click.echo(response.formatted_text)

    if save:
        from brief_evaluator.logger import save_result
        brief_text = brief.read_text(encoding="utf-8")
        save_result(response, brief_text)


if __name__ == "__main__":
    main()