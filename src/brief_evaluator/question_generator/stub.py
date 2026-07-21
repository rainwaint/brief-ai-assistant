from __future__ import annotations
from brief_evaluator.models import Brief, Question
from brief_evaluator.protocols import QuestionGenerator
from brief_evaluator.llm.base import BaseLLMClient


class StubQuestionGenerator(QuestionGenerator):
    def generate(self, brief: Brief) -> list[Question]:
        return [Question(text="Заглушка: вопрос 1", priority=1)]


class LLMQuestionGenerator(QuestionGenerator):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def generate(self, brief: Brief) -> list[Question]:
        goal = ""
        for section in brief.sections:
            if section.title == "Цель":
                goal = section.content[:300]
                break

        prompt = f"""
Проект: {brief.title}
Цель: {goal}

Сформулируй 3-5 конкретных вопросов к заказчику.
Каждый вопрос с новой строки.
"""
        system_prompt = "Ты — аналитик. Задавай конкретные вопросы на русском языке."

        response = self.llm.complete(prompt, system=system_prompt)
        questions = []
        for i, line in enumerate(response.splitlines(), start=1):
            line = line.strip()
            if line and len(line) > 5:
                questions.append(Question(text=line, priority=i))
        return questions[:5]
