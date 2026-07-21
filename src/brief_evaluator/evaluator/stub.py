from __future__ import annotations

import json
from brief_evaluator.models import Brief, CriteriaConfig, CriterionScore, EvaluationResult
from brief_evaluator.protocols import BriefEvaluator
from brief_evaluator.llm.base import BaseLLMClient


class StubBriefEvaluator(BriefEvaluator):
    def evaluate(self, brief: Brief, criteria: CriteriaConfig) -> EvaluationResult:
        scores = [CriterionScore(
            criterion_id=c.id,
            criterion_name=c.name,
            score=0.8,
            passed=True,
            comment="Заглушка"
        ) for c in criteria.criteria]
        return EvaluationResult(scores=scores, overall_score=0.8, passed=True, summary="Заглушка")


class LLMBriefEvaluator(BriefEvaluator):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm = llm_client

    def evaluate(self, brief: Brief, criteria: CriteriaConfig) -> EvaluationResult:
        brief_text = f"Название: {brief.title}\n"
        for section in brief.sections:
            brief_text += f"{section.title}: {section.content}\n"

        criteria_list = "\n".join([
            f"- {c.name} (id: {c.id}, порог: {c.threshold})"
            for c in criteria.criteria
        ])

        system_prompt = "Ты — эксперт по оценке брифов. Отвечай строго в формате JSON. Используй русский язык."
        user_prompt = f"""
Оцени бриф по каждому критерию. Верни JSON:
{{
    "scores": [
        {{"criterion_id": "has_goal", "score": 0.8, "comment": "краткий комментарий"}},
        ...
    ],
    "summary": "общий вывод"
}}

Критерии:
{criteria_list}

Бриф:
{brief_text}
"""
        response = self.llm.complete(user_prompt, system=system_prompt)
        try:
            data = json.loads(response)
        except:
            return self._fallback_evaluation(criteria)

        scores = []
        for c in criteria.criteria:
            found = next((s for s in data.get("scores", []) if s.get("criterion_id") == c.id), None)
            if found:
                score = max(0.0, min(1.0, float(found.get("score", 0.5))))
                comment = found.get("comment", "")
            else:
                score = 0.5
                comment = "Оценка не найдена"
            scores.append(
                CriterionScore(
                    criterion_id=c.id,
                    criterion_name=c.name,
                    score=score,
                    passed=score >= c.threshold,
                    comment=comment,
                )
            )

        overall = sum(s.score * next(c.weight for c in criteria.criteria if c.id == s.criterion_id) for s in scores)
        overall = overall / criteria.total_weight if criteria.total_weight > 0 else 0.5
        passed = overall >= 0.6

        return EvaluationResult(
            scores=scores,
            overall_score=overall,
            passed=passed,
            summary=data.get("summary", f"Общий балл: {overall:.2f}"),
        )

    def _fallback_evaluation(self, criteria: CriteriaConfig) -> EvaluationResult:
        scores = [CriterionScore(
            criterion_id=c.id,
            criterion_name=c.name,
            score=0.5,
            passed=False,
            comment="Оценка по умолчанию"
        ) for c in criteria.criteria]
        return EvaluationResult(scores=scores, overall_score=0.5, passed=False, summary="Ошибка оценки")