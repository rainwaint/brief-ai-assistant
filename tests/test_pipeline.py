"""Tests for the evaluation pipeline."""

from brief_evaluator.pipeline import EvaluationPipeline


def test_pipeline_runs_end_to_end(
    pipeline: EvaluationPipeline,
    sample_brief_text: str,
    sample_tz_text: str,
) -> None:
    response = pipeline.run(sample_brief_text, technical_spec=sample_tz_text)

    assert response.brief_title
    assert response.evaluation.scores
    assert response.questions
    assert response.mvp.features
    assert "Оценка брифа" in response.formatted_text


def test_pipeline_from_files(
    pipeline: EvaluationPipeline,
    tmp_path,
    sample_brief_text: str,
    sample_tz_text: str,
) -> None:
    brief_file = tmp_path / "brief.txt"
    tz_file = tmp_path / "tz.txt"
    brief_file.write_text(sample_brief_text, encoding="utf-8")
    tz_file.write_text(sample_tz_text, encoding="utf-8")

    response = pipeline.run_from_files(brief_file, tz_path=tz_file)

    assert response.evaluation.overall_score > 0
    assert response.mvp.title.startswith("MVP:")
