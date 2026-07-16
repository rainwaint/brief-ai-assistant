"""Pydantic models for brief evaluation pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BriefSection(BaseModel):
    """A named section extracted from a brief."""

    title: str
    content: str


class Brief(BaseModel):
    """Structured representation of a project brief."""

    title: str
    summary: str
    sections: list[BriefSection] = Field(default_factory=list)
    raw_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Criterion(BaseModel):
    """A single evaluation criterion."""

    id: str
    name: str
    description: str
    weight: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0, default=0.7)

    @field_validator("weight")
    @classmethod
    def weight_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("weight must be greater than 0")
        return value


class CriteriaConfig(BaseModel):
    """Collection of evaluation criteria loaded from configuration."""

    name: str
    description: str = ""
    criteria: list[Criterion]

    @field_validator("criteria")
    @classmethod
    def criteria_must_not_be_empty(cls, value: list[Criterion]) -> list[Criterion]:
        if not value:
            raise ValueError("criteria list must not be empty")
        return value

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.criteria)


class CriterionScore(BaseModel):
    """Score for a single criterion."""

    criterion_id: str
    criterion_name: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    comment: str = ""


class EvaluationResult(BaseModel):
    """Aggregated evaluation of a brief against criteria."""

    scores: list[CriterionScore]
    overall_score: float = Field(ge=0.0, le=1.0)
    passed: bool
    summary: str = ""


class Question(BaseModel):
    """A clarifying question generated for the brief author."""

    text: str
    related_criterion_id: str | None = None
    priority: int = Field(ge=1, le=5, default=3)


class MVPSuggestion(BaseModel):
    """Suggested minimum viable product scope."""

    title: str
    description: str
    features: list[str] = Field(default_factory=list)
    rationale: str = ""


class AssistantResponse(BaseModel):
    """Final output of the evaluation pipeline."""

    brief_title: str
    evaluation: EvaluationResult
    questions: list[Question]
    mvp: MVPSuggestion
    formatted_text: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
