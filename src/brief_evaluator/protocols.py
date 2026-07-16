"""Protocol and abstract base class interfaces for all pipeline components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from brief_evaluator.models import (
    AssistantResponse,
    Brief,
    CriteriaConfig,
    EvaluationResult,
    MVPSuggestion,
    Question,
)


@runtime_checkable
class LLMClient(Protocol):
    """Abstraction over an LLM provider."""

    def complete(self, prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
        """Return a text completion for the given prompt."""
        ...

    def complete_structured(
        self,
        prompt: str,
        schema: type[Any],
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Return a structured response validated against the given schema."""
        ...


class BriefExtractor(ABC):
    """Extracts structured brief data from raw input."""

    @abstractmethod
    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        """Parse raw brief text into a structured Brief model."""
        ...

    @abstractmethod
    def extract_from_file(
        self,
        path: Path,
        *,
        technical_spec: str | None = None,
    ) -> Brief:
        """Load and extract a brief from a file."""
        ...


class BriefEvaluator(ABC):
    """Evaluates a brief against criteria derived from a technical specification."""

    @abstractmethod
    def evaluate(
        self,
        brief: Brief,
        criteria: CriteriaConfig,
        *,
        technical_spec: str | None = None,
    ) -> EvaluationResult:
        """Score the brief against the provided criteria."""
        ...


class QuestionGenerator(ABC):
    """Generates clarifying questions based on evaluation gaps."""

    @abstractmethod
    def generate(
        self,
        brief: Brief,
        evaluation: EvaluationResult,
        *,
        technical_spec: str | None = None,
    ) -> list[Question]:
        """Produce clarifying questions for identified gaps."""
        ...


class MVPSuggester(ABC):
    """Suggests a minimum viable product scope."""

    @abstractmethod
    def suggest(
        self,
        brief: Brief,
        evaluation: EvaluationResult,
        *,
        technical_spec: str | None = None,
    ) -> MVPSuggestion:
        """Propose an MVP scope based on the brief and evaluation."""
        ...


class ResponseWriter(ABC):
    """Formats the final assistant response."""

    @abstractmethod
    def write(
        self,
        brief: Brief,
        evaluation: EvaluationResult,
        questions: list[Question],
        mvp: MVPSuggestion,
    ) -> AssistantResponse:
        """Compose the final structured response."""
        ...


class CriteriaProvider(ABC):
    """Loads evaluation criteria from a configuration source."""

    @abstractmethod
    def load(self) -> CriteriaConfig:
        """Return the criteria configuration."""
        ...

    @abstractmethod
    def load_from_path(self, path: Path) -> CriteriaConfig:
        """Load criteria from a specific file path."""
        ...
