from __future__ import annotations

import json
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from brief_evaluator.llm.base import BaseLLMClient


class OllamaLLMClient(BaseLLMClient):
    """LLM client for local Ollama server via OpenAI-compatible API."""

    def __init__(
        self,
        model: str = "mistral",
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.1,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self._llm = ChatOpenAI(
            openai_api_key="fake-key",  # Ollama не требует ключа
            base_url=self.base_url,
            model_name=self.model,
            temperature=self.temperature,
        )

    def complete(self, prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
        messages = []
        if system:
            messages.append(("system", system))
        messages.append(("human", prompt))
        response = self._llm.invoke(messages)
        return response.content

    def complete_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> BaseModel:
        response = self.complete(prompt, system=system)
        try:
            data = json.loads(response)
            return schema.model_validate(data)
        except json.JSONDecodeError:
            return schema.model_validate({})