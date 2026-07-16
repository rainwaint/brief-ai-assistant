"""Evaluate brief against criteria (stub + LLM)."""

from __future__ import annotations

import json

from brief_evaluator.models import (
    Brief,
    CriteriaConfig,
    CriterionScore,
    EvaluationResult,
)
from brief_evaluator.protocols import BriefEvaluator
from brief_evaluator.llm.base import BaseLLMClient


# --- Старая заглушка для обратной совместимости ---
class StubBriefEvaluator(BriefEvaluator):
    """Stub evaluator that returns dummy scores."""

    def evaluate(self, brief: Brief, criteria: CriteriaConfig) -> EvaluationResult:
        # Простая заглушка: все критерии проходят
        scores = [
            CriterionScore(
                criterion_id=c.id,
                criterion_name=c.name,
                score=0.8,
                passed=True,
                comment=f"Заглушка: критерий {c.name} пройден",
            )
            for c in criteria.criteria
        ]
        return EvaluationResult(
            scores=scores,
            overall_score=0.8,
            passed=True,
            summary="Заглушка: проект соответствует критериям",
        )


# --- Новая LLM-реализация ---
class LLMBriefEvaluator(BriefEvaluator):
    """Evaluates brief against arbitrary criteria using LLM."""

    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def evaluate(self, brief: Brief, criteria: CriteriaConfig) -> EvaluationResult:
        scores = []
        total_weight = criteria.total_weight
        weighted_sum = 0.0

        # Собираем содержимое брифа в читаемый вид
        brief_text = f"Название: {brief.title}\n"
        for section in brief.sections:
            brief_text += f"{section.title}: {section.content}\n"

        for criterion in criteria.criteria:
            system_prompt = (
                "Ты — эксперт по оценке проектных брифов. "
                "Отвечай только в формате JSON с полями: score (число от 0 до 1) и comment (строка)."
                "Отвечай строго на русском языке."
            )
            user_prompt = f"""
Оцени следующий бриф по критерию:

**Критерий:** {criterion.name}
**Описание:** {criterion.description}

**Бриф:**
{brief_text}

Выставь оценку от 0 до 1, где 0 — полностью не соответствует, 1 — полностью соответствует.
Также дай краткий комментарий (1–2 предложения).

Ответь JSON:
{{"score": 0.8, "comment": "Цель сформулирована чётко, но задачи не конкретизированы"}}
"""
            response = self.llm.complete(user_prompt, system=system_prompt)
            try:
                data = json.loads(response)
                score = max(0.0, min(1.0, float(data.get("score", 0.5))))
                comment = data.get("comment", "")
            except (json.JSONDecodeError, ValueError, KeyError):
                score = 0.5
                comment = "Не удалось оценить критерий"

            passed = score >= criterion.threshold
            weighted_score = score * criterion.weight
            weighted_sum += weighted_score

            scores.append(
                CriterionScore(
                    criterion_id=criterion.id,
                    criterion_name=criterion.name,
                    score=score,
                    passed=passed,
                    comment=comment,
                )
            )

        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        passed = overall_score >= 0.7  # общий порог можно вынести в конфиг

        summary = f"Общий балл: {overall_score:.2f}. " + (
            "Проект соответствует критериям." if passed else "Требуется доработка."
        )

        return EvaluationResult(
            scores=scores,
            overall_score=overall_score,
            passed=passed,
            summary=summary,
        )