import json
import re
from pathlib import Path
from brief_evaluator.models import Brief, BriefSection
from brief_evaluator.protocols import BriefExtractor
from brief_evaluator.llm.base import BaseLLMClient


class StubBriefExtractor(BriefExtractor):
    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        return Brief(
            title="Тестовый проект (заглушка)",
            summary="Заглушка",
            sections=[BriefSection(title="Цель", content="Тест")],
            raw_text=raw_text,
            metadata={"source": "stub"},
        )

    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        return self.extract(raw_text, technical_spec=technical_spec)


class LLMBriefExtractor(BriefExtractor):
    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client

    def extract(self, raw_text: str, *, technical_spec: str | None = None) -> Brief:
        system_prompt = "Ты — эксперт по извлечению данных из брифов. Отвечай строго в формате JSON. Используй русский язык."
        user_prompt = f"""
Извлеки из брифа данные и верни JSON:
{{
    "title": "название проекта",
    "goal": "цель проекта",
    "expected_result": "ожидаемый результат",
    "tasks": ["задача 1", "задача 2"],
    "domain": "предметная область",
    "direction": "development | design | analytics | marketing | ai | education | mixed",
    "available_materials": ["материал 1"],
    "missing_information": ["чего не хватает"],
    "complexity_factors": ["факторы сложности"]
}}

Текст брифа:
{raw_text}
"""
        response = self.llm.complete(user_prompt, system=system_prompt)
        try:
            data = json.loads(response)
        except:
            data = {}

        title = data.get("title", "Без названия")
        goal = data.get("goal", "")
        expected = data.get("expected_result", "")
        tasks = data.get("tasks", [])
        domain = data.get("domain", "")
        direction = data.get("direction", "mixed")
        materials = data.get("available_materials", [])
        missing = data.get("missing_information", [])
        complexity = data.get("complexity_factors", [])

        sections = [
            BriefSection(title="Цель", content=goal),
            BriefSection(title="Ожидаемый результат", content=expected),
            BriefSection(title="Задачи", content=", ".join(tasks)),
            BriefSection(title="Предметная область", content=domain),
            BriefSection(title="Направление", content=direction),
            BriefSection(title="Доступные материалы", content=", ".join(materials)),
            BriefSection(title="Отсутствующая информация", content=", ".join(missing)),
            BriefSection(title="Факторы сложности", content=", ".join(complexity)),
        ]
        return Brief(
            title=title,
            summary=f"Извлечено через LLM",
            sections=sections,
            raw_text=raw_text,
            metadata={"source": "llm"},
        )

    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        return self.extract(raw_text, technical_spec=technical_spec)