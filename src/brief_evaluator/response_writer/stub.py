"""Write a draft response to the customer (stub + LLM)."""

from __future__ import annotations

from brief_evaluator.models import Brief, EvaluationResult
from brief_evaluator.protocols import ResponseWriter
from brief_evaluator.llm.base import BaseLLMClient


# --- Старая заглушка ---
class StubResponseWriter(ResponseWriter):
    """Stub response writer returning dummy draft."""

    def write(self, brief: Brief, evaluation: EvaluationResult) -> str:
        return "Заглушка: черновик ответа заказчику."


# --- Новая LLM-реализация ---
class LLMResponseWriter(ResponseWriter):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def write(self, brief: Brief, evaluation: EvaluationResult) -> str:
        goal = ""
        for section in brief.sections:
            if section.title == "Цель":
                goal = section.content
                break

        prompt = f"""
Напиши черновик делового письма заказчику на основе оценки проекта.

Описание проекта: {goal}
Результат оценки: {"Пройдено" if evaluation.passed else "Не пройдено"}
Общий балл: {evaluation.overall_score:.2f}
Комментарии по критериям:
{self._format_scores(evaluation.scores)}

Требования к письму:
- Тон — вежливый, деловой, бережный.
- Объясни, почему проект принимается или требует доработки.
- Если есть замечания — сформулируй их конструктивно.
- Предложи следующие шаги.

Письмо должно быть готово к отправке.
"""
        return self.llm.complete(prompt, system="Ты — менеджер проекта, пишешь письма заказчикам. Отвечай строго на русском языке.")

    def _format_scores(self, scores) -> str:
        lines = []
        for s in scores:
            status = "✅" if s.passed else "❌"
            lines.append(f"{status} {s.criterion_name}: {s.comment} (оценка {s.score:.0%})")
        return "\n".join(lines)
