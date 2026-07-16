"""Tests for criteria configuration loading."""

from pathlib import Path

import pytest

from brief_evaluator.config import YamlCriteriaProvider


def test_load_default_criteria(criteria_path: Path) -> None:
    provider = YamlCriteriaProvider(criteria_path)
    config = provider.load()

    assert config.name == "default"
    assert len(config.criteria) == 4
    assert config.total_weight == pytest.approx(1.0)


def test_load_from_path(criteria_path: Path) -> None:
    config = YamlCriteriaProvider().load_from_path(criteria_path)
    ids = {criterion.id for criterion in config.criteria}
    assert ids == {"completeness", "clarity", "feasibility", "alignment"}