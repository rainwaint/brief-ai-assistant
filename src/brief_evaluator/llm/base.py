"""Abstract base class for LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseLLMClient(ABC):
    """Abstract LLM client implementing the LLMClient protocol."""

    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
        """Return a text completion for the given prompt."""

    @abstractmethod
    def complete_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> BaseModel:
        """Return a structured response validated against the given Pydantic schema."""
