from __future__ import annotations
from brief_evaluator.models import Brief, MVPSuggestion
from brief_evaluator.protocols import MVPSuggester
from brief_evaluator.llm.base import BaseLLMClient


class StubMVPSuggester(MVPSuggester):
    def suggest(self, brief: Brief) -> MVPSuggestion:
        return MVPSuggestion(title="Заглушка MVP", description="Описание", features=["Фича 1"], rationale="Обоснование")


class LLMMVPSuggester(MVPSuggester):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def suggest(self, brief: Brief) -> MVPSuggestion:
        goal = ""
        tasks = ""
        for section in brief.sections:
            if section.title == "Цель":
                goal = section.content[:300]
            if section.title == "Задачи":
                tasks = section.content[:300]

        prompt = f"""
Проект: {brief.title}
Цель: {goal}
Задачи: {tasks}

Предложи MVP (минимальную версию). Ответь:
- Название MVP
- 2-3 ключевые функции
- Почему это реалистично для студентов
"""
        system_prompt = "Ты — архитектор. Отвечай кратко на русском языке."

        response = self.llm.complete(prompt, system=system_prompt)
        lines = response.splitlines()
        title = "MVP"
        features = []
        rationale = ""

        for line in lines:
            line = line.strip()
            if "название" in line.lower():
                title = line.split(":", 1)[-1].strip() if ":" in line else line
            elif "функции" in line.lower() or "реалистич" in line.lower():
                if ":" in line:
                    features.append(line.split(":", 1)[-1].strip())
                else:
                    features.append(line)
            elif "обоснован" in line.lower() or "почему" in line.lower():
                rationale = line

        return MVPSuggestion(
            title=title,
            description=response[:300],
            features=features[:3],
            rationale=rationale or "MVP предложен на основе брифа.",
        )