"""Extract structured data from brief using LLM (or stub)."""

from __future__ import annotations

import json
from pathlib import Path

from brief_evaluator.models import Brief, BriefSection
from brief_evaluator.protocols import BriefExtractor
from brief_evaluator.llm.base import BaseLLMClient

import re

class RegexBriefExtractor(BriefExtractor):
    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        # Ищем ключевые разделы
        patterns = {
            "title": r"Название[:\s]+(.+?)(?:\n|$)",
            "goal": r"Цель[:\s]+(.+?)(?:\n|$)",
            "expected": r"Ожидаемый результат[:\s]+(.+?)(?:\n|$)",
            "tasks": r"Задачи[:\s]+(.+?)(?:\n|$)",
            "domain": r"Предметная область[:\s]+(.+?)(?:\n|$)",
            "direction": r"Направление[:\s]+(.+?)(?:\n|$)",
            "materials": r"Доступные материалы[:\s]+(.+?)(?:\n|$)",
            "missing": r"Отсутствующая информация[:\s]+(.+?)(?:\n|$)",
            "complexity": r"Факторы сложности[:\s]+(.+?)(?:\n|$)",
        }
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            data[key] = match.group(1).strip() if match else ""

        # Преобразуем в Brief
        sections = [
            BriefSection(title="Цель", content=data.get("goal", "")),
            BriefSection(title="Ожидаемый результат", content=data.get("expected", "")),
            BriefSection(title="Задачи", content=data.get("tasks", "")),
            BriefSection(title="Предметная область", content=data.get("domain", "")),
            BriefSection(title="Направление", content=data.get("direction", "mixed")),
            BriefSection(title="Доступные материалы", content=data.get("materials", "")),
            BriefSection(title="Отсутствующая информация", content=data.get("missing", "")),
            BriefSection(title="Факторы сложности", content=data.get("complexity", "")),
        ]
        return Brief(
            title=data.get("title", "Без названия"),
            summary=f"Извлечено из брифа с помощью regex ({len(raw_text)} символов)",
            sections=sections,
            raw_text=raw_text,
            metadata={"source": "regex", "has_technical_spec": technical_spec is not None},
        )
    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        brief = self.extract(raw_text, technical_spec=technical_spec)
        brief.metadata["source_path"] = str(path)
        return brief


# --- Старая заглушка для обратной совместимости ---
class StubBriefExtractor(BriefExtractor):
    """Extracts placeholder structured data from raw brief text."""

    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        title = self._infer_title(raw_text)
        return Brief(
            title=title,
            summary=f"Краткое описание брифа ({len(raw_text)} символов)",
            sections=[
                BriefSection(title="Цели", content="Заглушка: цели проекта"),
                BriefSection(title="Аудитория", content="Заглушка: целевая аудитория"),
            ],
            raw_text=raw_text,
            metadata={"source": "stub", "has_technical_spec": technical_spec is not None},
        )

    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        brief = self.extract(raw_text, technical_spec=technical_spec)
        brief.metadata["source_path"] = str(path)
        return brief

    @staticmethod
    def _infer_title(raw_text: str) -> str:
        for line in raw_text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:120]
        return "Без названия"


# --- Новая LLM-реализация ---
class LLMBriefExtractor(BriefExtractor):
    """Extracts structured data from brief via LLM with a prompt."""

    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        # ... (оставь код, который уже есть)
        system_prompt = (
            "Ты — эксперт по извлечению структурированной информации из проектных брифов. "
            "Отвечай только в формате JSON без дополнительных пояснений."
        )
        user_prompt = f"""
Извлеки из брифа:
- Название проекта
- Цель
- Ожидаемый результат
- Задачи (список через запятую)
- Предметная область
- Направление (development/design/analytics/marketing/ai/education/mixed)
- Доступные материалы
- Отсутствующая информация
- Факторы сложности

Ответ дай в виде списка:
Название: ...
Цель: ...
...
"""
        response = self.llm.complete(user_prompt, system=system_prompt)
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = {
                "title": "Ошибка парсинга",
                "goal": "Не удалось извлечь данные",
                "expected_result": "",
                "tasks": [],
                "domain": "",
                "direction": "mixed",
                "available_materials": [],
                "missing_information": ["Не удалось распарсить ответ модели"],
                "complexity_factors": [],
            }

        sections = [
            BriefSection(title="Цель", content=data.get("goal", "")),
            BriefSection(title="Ожидаемый результат", content=data.get("expected_result", "")),
            BriefSection(title="Задачи", content=", ".join(data.get("tasks", []))),
            BriefSection(title="Предметная область", content=data.get("domain", "")),
            BriefSection(title="Направление", content=data.get("direction", "")),
            BriefSection(title="Доступные материалы", content=", ".join(data.get("available_materials", []))),
            BriefSection(title="Отсутствующая информация", content=", ".join(data.get("missing_information", []))),
            BriefSection(title="Факторы сложности", content=", ".join(data.get("complexity_factors", []))),
        ]
        return Brief(
            title=data.get("title", "Без названия"),
            summary=f"Извлечено из брифа ({len(raw_text)} символов)",
            sections=sections,
            raw_text=raw_text,
            metadata={
                "source": "llm",
                "has_technical_spec": technical_spec is not None,
                "extracted_direction": data.get("direction"),
            },
        )

    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        brief = self.extract(raw_text, technical_spec=technical_spec)
        brief.metadata["source_path"] = str(path)
        return brief