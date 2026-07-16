"""Suggest MVP simplification (stub + LLM)."""

from __future__ import annotations

from brief_evaluator.models import Brief, MVPSuggestion
from brief_evaluator.protocols import MVPSuggester
from brief_evaluator.llm.base import BaseLLMClient


# --- Старая заглушка ---
class StubMVPSuggester(MVPSuggester):
    """Stub MVP suggester returning dummy suggestion."""

    def suggest(self, brief: Brief) -> MVPSuggestion:
        return MVPSuggestion(
            title="Заглушка MVP",
            description="Это заглушка для предложения MVP",
            features=["Фича 1", "Фича 2"],
            rationale="Заглушка: обоснование",
        )


# --- Новая LLM-реализация ---
class LLMMVPSuggester(MVPSuggester):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def suggest(self, brief: Brief) -> MVPSuggestion:
        goal = ""
        tasks = ""
        for section in brief.sections:
            if section.title == "Цель":
                goal = section.content
            if section.title == "Задачи":
                tasks = section.content

        prompt = f"""
На основе следующего проектного брифа предложи минимально жизнеспособный продукт (MVP) для студенческой команды.

Цель проекта: {goal}
Задачи: {tasks}

Опиши:
1. Название MVP.
2. Краткое описание того, что будет сделано в первой версии.
3. Список ключевых функций, которые войдут в MVP (каждая функция с новой строки).
4. Обоснование, почему именно такой объём работ реалистичен для студентов.

Ответ дай в виде структурированного текста с явными разделами: "Название:", "Описание:", "Функции:", "Обоснование:".
Отвечай строго на русском языке.
"""
        response = self.llm.complete(prompt, system="Ты — опытный архитектор, помогаешь выбрать реалистичный MVP.")

        # Парсим ответ, чтобы заполнить поля MVPSuggestion
        title = "MVP"
        description = response.strip()
        features = []
        rationale = ""

        lines = response.splitlines()
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("Название:"):
                title = line.replace("Название:", "").strip()
            elif line.startswith("Описание:"):
                description = line.replace("Описание:", "").strip()
            elif line.startswith("Функции:"):
                current_section = "features"
            elif line.startswith("Обоснование:"):
                current_section = "rationale"
                rationale = line.replace("Обоснование:", "").strip()
            elif current_section == "features" and line:
                if not line.startswith(("Название", "Описание", "Обоснование")):
                    features.append(line)
            elif current_section == "rationale" and line:
                rationale += " " + line

        return MVPSuggestion(
            title=title,
            description=description,
            features=features,
            rationale=rationale,
        )
