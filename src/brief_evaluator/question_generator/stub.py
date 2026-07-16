"""Generate clarifying questions (stub + LLM)."""

from __future__ import annotations

from brief_evaluator.models import Brief, Question
from brief_evaluator.protocols import QuestionGenerator
from brief_evaluator.llm.base import BaseLLMClient


# --- Старая заглушка ---
class StubQuestionGenerator(QuestionGenerator):
    """Stub question generator returning dummy questions."""

    def generate(self, brief: Brief) -> list[Question]:
        return [
            Question(text="Заглушка: вопрос 1", priority=1),
            Question(text="Заглушка: вопрос 2", priority=2),
        ]


# --- Новая LLM-реализация ---
class LLMQuestionGenerator(QuestionGenerator):
    """Generates questions based on missing information in the brief."""

    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def generate(self, brief: Brief) -> list[Question]:
        # Извлекаем отсутствующую информацию
        missing = ""
        for section in brief.sections:
            if section.title == "Отсутствующая информация":
                missing = section.content
                break

        prompt = f"""
На основе брифа сформулируй 3–5 конкретных вопросов к заказчику, чтобы прояснить недостающие моменты.
Особое внимание удели тому, что не указано: {missing if missing else "явно не хватает деталей"}.
Отвечай строго на русском языке.

Верни ответ в виде списка строк (каждая строка — отдельный вопрос). Без нумерации, просто вопросы.
"""
        response = self.llm.complete(prompt, system="Ты — аналитик, задаёшь уточняющие вопросы.")
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        questions = []
        for i, line in enumerate(lines[:5], start=1):
            questions.append(Question(text=line, priority=i))
        return questions
