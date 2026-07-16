"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from brief_evaluator.models import (
    AssistantResponse,
    Brief,
    BriefSection,
    CriteriaConfig,
    Criterion,
    CriterionScore,
    EvaluationResult,
    MVPSuggestion,
    Question,
)


def test_brief_model_validates() -> None:
    brief = Brief(
        title="Test Brief",
        summary="Summary",
        sections=[BriefSection(title="Goals", content="Launch MVP")],
        raw_text="raw",
    )
    assert brief.title == "Test Brief"
    assert len(brief.sections) == 1


def test_criterion_weight_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Criterion(
            id="x",
            name="X",
            description="desc",
            weight=0.0,
            threshold=0.5,
        )


def test_criteria_config_requires_criteria() -> None:
    with pytest.raises(ValidationError):
        CriteriaConfig(name="empty", criteria=[])


def test_evaluation_result_validates_scores() -> None:
    result = EvaluationResult(
        scores=[
            CriterionScore(
                criterion_id="c1",
                criterion_name="Clarity",
                score=0.8,
                passed=True,
            )
        ],
        overall_score=0.8,
        passed=True,
    )
    assert result.overall_score == 0.8


def test_assistant_response_roundtrip() -> None:
    evaluation = EvaluationResult(
        scores=[
            CriterionScore(
                criterion_id="c1",
                criterion_name="Test",
                score=0.7,
                passed=True,
            )
        ],
        overall_score=0.7,
        passed=True,
    )
    response = AssistantResponse(
        brief_title="Brief",
        evaluation=evaluation,
        questions=[Question(text="Why?")],
        mvp=MVPSuggestion(title="MVP", description="Scope"),
        formatted_text="# Output",
    )
    restored = AssistantResponse.model_validate(response.model_dump())
    assert restored.brief_title == "Brief"
