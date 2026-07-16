"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from brief_evaluator.config import YamlCriteriaProvider
from brief_evaluator.evaluator.stub import StubBriefEvaluator
from brief_evaluator.extractor.stub import StubBriefExtractor
from brief_evaluator.mvp_suggester.stub import StubMVPSuggester
from brief_evaluator.pipeline import EvaluationPipeline
from brief_evaluator.question_generator.stub import StubQuestionGenerator
from brief_evaluator.response_writer.stub import StubResponseWriter


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def criteria_path(project_root: Path) -> Path:
    return project_root / "config" / "criteria.yaml"


@pytest.fixture
def sample_brief_text() -> str:
    return "Мобильное приложение для доставки\n\nОписание проекта и цели."


@pytest.fixture
def sample_tz_text() -> str:
    return "Техническое задание\n\nТребования к системе и ограничения."


@pytest.fixture
def pipeline(criteria_path: Path) -> EvaluationPipeline:
    provider = YamlCriteriaProvider(criteria_path)
    return EvaluationPipeline(
        extractor=StubBriefExtractor(),
        evaluator=StubBriefEvaluator(),
        question_generator=StubQuestionGenerator(),
        mvp_suggester=StubMVPSuggester(),
        response_writer=StubResponseWriter(),
        criteria_provider=provider,
    )
