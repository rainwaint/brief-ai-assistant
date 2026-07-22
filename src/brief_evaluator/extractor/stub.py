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
        system_prompt = "Ты — эксперт по извлечению данных из брифов. Отвечай кратко. Используй русский язык."

        user_prompt = f"""
    Извлеки из брифа:

    1. Название проекта
    2. Цель проекта
    3. Ожидаемый результат
    4. Задачи (через запятую)
    5. Предметная область
    6. Направление (development, design, analytics, marketing, ai, education, mixed)
    7. Доступные материалы
    8. Отсутствующая информация
    9. Факторы сложности

    Ответь списком (каждый пункт с новой строки):
    Название: ...
    Цель: ...
    ...
    """
        response = self.llm.complete(user_prompt, system=system_prompt)

        # Парсим ответ
        data = {}
        for line in response.splitlines():
            line = line.strip()
            if "Название:" in line:
                data["title"] = line.replace("Название:", "").strip()
            elif "Цель:" in line:
                data["goal"] = line.replace("Цель:", "").strip()
            elif "Ожидаемый результат:" in line:
                data["expected_result"] = line.replace("Ожидаемый результат:", "").strip()
            elif "Задачи:" in line:
                data["tasks"] = line.replace("Задачи:", "").strip()
            elif "Предметная область:" in line:
                data["domain"] = line.replace("Предметная область:", "").strip()
            elif "Направление:" in line:
                data["direction"] = line.replace("Направление:", "").strip()
            elif "Доступные материалы:" in line:
                data["available_materials"] = line.replace("Доступные материалы:", "").strip()
            elif "Отсутствующая информация:" in line:
                data["missing_information"] = line.replace("Отсутствующая информация:", "").strip()
            elif "Факторы сложности:" in line:
                data["complexity_factors"] = line.replace("Факторы сложности:", "").strip()

        # Заполняем значения
        title = data.get("title", "Без названия")
        goal = data.get("goal", "")
        expected = data.get("expected_result", "")
        tasks = [t.strip() for t in data.get("tasks", "").split(",") if t.strip()]
        domain = data.get("domain", "")
        direction = data.get("direction", "mixed")
        materials = [m.strip() for m in data.get("available_materials", "").split(",") if m.strip()]
        missing = [m.strip() for m in data.get("missing_information", "").split(",") if m.strip()]
        complexity = [c.strip() for c in data.get("complexity_factors", "").split(",") if c.strip()]

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
            summary=f"Извлечено через LLM ({len(raw_text)} символов)",
            sections=sections,
            raw_text=raw_text,
            metadata={"source": "llm"},
        )

    def extract_from_file(self, path: Path, *, technical_spec: str | None = None) -> Brief:
        raw_text = path.read_text(encoding="utf-8")
        return self.extract(raw_text, technical_spec=technical_spec)