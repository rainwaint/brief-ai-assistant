"""Stub LLM client for development and testing."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from brief_evaluator.llm.base import BaseLLMClient


class StubLLMClient(BaseLLMClient):
    """Returns placeholder completions without calling a real LLM."""

    def complete(self, prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
        prefix = f"[stub:{system}] " if system else "[stub] "
        return f"{prefix}Ответ-заглушка для запроса длиной {len(prompt)} символов."

    def complete_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> BaseModel:
        fields = schema.model_fields
        payload: dict[str, Any] = {}
        for name, field in fields.items():
            annotation = field.annotation
            if annotation is str:
                payload[name] = f"stub-{name}"
            elif annotation is int:
                payload[name] = 1
            elif annotation is float:
                payload[name] = 0.5
            elif annotation is bool:
                payload[name] = True
            elif getattr(annotation, "__origin__", None) is list:
                payload[name] = []
            else:
                payload[name] = None
        return schema.model_validate(payload)
