from __future__ import annotations
from brief_evaluator.models import Brief, EvaluationResult
from brief_evaluator.protocols import ResponseWriter
from brief_evaluator.llm.base import BaseLLMClient


class StubResponseWriter(ResponseWriter):
    def write(self, brief: Brief, evaluation: EvaluationResult) -> str:
        return "Заглушка: черновик ответа."


class LLMResponseWriter(ResponseWriter):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def write(self, brief: Brief, evaluation: EvaluationResult) -> str:
        goal = ""
        for section in brief.sections:
            if section.title == "Цель":
                goal = section.content[:300]
                break

        prompt = f"""
Проект: {brief.title}
Цель: {goal}
Оценка: {"пройдено" if evaluation.passed else "не пройдено"}
Балл: {evaluation.overall_score:.2f}

Напиши краткое письмо заказчику (2-3 абзаца) с рекомендациями.
Тон — деловой, вежливый. На русском языке.
"""
        system_prompt = "Ты — менеджер проекта. Пиши кратко и по делу."

        return self.llm.complete(prompt, system=system_prompt)
