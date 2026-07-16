from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from brief_evaluator.llm.base import BaseLLMClient

load_dotenv()


class OpenRouterLLMClient(BaseLLMClient):
    """LLM client using OpenRouter API via langchain."""

    def __init__(
        self,
        model: str = "openrouter/free",
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.3,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url
        self.temperature = temperature

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY не найден. Убедитесь, что он указан в .env файле."
            )

        self._llm = ChatOpenAI(
            openai_api_key=self.api_key,
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