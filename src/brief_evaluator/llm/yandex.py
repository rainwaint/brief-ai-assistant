from __future__ import annotations

import json
import os
import requests
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from brief_evaluator.llm.base import BaseLLMClient

load_dotenv()


class YandexGPTClient(BaseLLMClient):
    """Клиент для YandexGPT через OpenAI-совместимый API."""

    def __init__(
        self,
        model: str = "yandexgpt-lite",
        api_key: str | None = None,
        folder_id: str | None = None,
        temperature: float = 0.3,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or os.getenv("YANDEX_API_KEY")
        self.folder_id = folder_id or os.getenv("YANDEX_FOLDER_ID")

        if not self.api_key:
            raise ValueError("YANDEX_API_KEY не найден. Укажите его в .env")
        if not self.folder_id:
            raise ValueError("YANDEX_FOLDER_ID не найден. Укажите его в .env")

        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, prompt: str, *, system: str | None = None, **kwargs: Any) -> str:
        url = "https://llm.api.cloud.yandex.net/v1/chat/completions"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json",
        }

        payload = {
            "model": f"gpt://{self.folder_id}/{self.model}",
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 1000,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)

        if response.status_code != 200:
            raise Exception(f"YandexGPT ошибка: {response.status_code} - {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

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