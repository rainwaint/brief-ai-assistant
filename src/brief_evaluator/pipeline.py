"""Main pipeline orchestrating all steps."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from brief_evaluator.models import (
    Brief,
    CriteriaConfig,
    EvaluationResult,
    Question,
    MVPSuggestion,
    AssistantResponse,
)
from brief_evaluator.protocols import (
    BriefExtractor,
    BriefEvaluator,
    QuestionGenerator,
    MVPSuggester,
    ResponseWriter,
    CriteriaProvider,
)


class EvaluationPipeline:
    def __init__(
        self,
        extractor: BriefExtractor,
        evaluator: BriefEvaluator,
        question_generator: QuestionGenerator,
        mvp_suggester: MVPSuggester,
        response_writer: ResponseWriter,
        criteria_provider: CriteriaProvider,
    ) -> None:
        self.extractor = extractor
        self.evaluator = evaluator
        self.question_generator = question_generator
        self.mvp_suggester = mvp_suggester
        self.response_writer = response_writer
        self.criteria_provider = criteria_provider

    def run(self, raw_text: str, *, technical_spec: str | None = None) -> AssistantResponse:
        print("1. Загрузка критериев...")
        criteria = self.criteria_provider.load()
        print("   Критерии загружены")
    
        print("2. Извлечение данных из брифа...")
        brief = self.extractor.extract(raw_text, technical_spec=technical_spec)
        print("   Извлечено: название =", brief.title)
    
        print("3. Оценка по критериям...")
        evaluation = self.evaluator.evaluate(brief, criteria)
        print("   Оценка пройдена:", evaluation.passed)
    
        print("4. Генерация уточняющих вопросов...")
        questions = self.question_generator.generate(brief)
        print("   Сгенерировано вопросов:", len(questions))
    
        print("5. Предложение MVP...")
        mvp = self.mvp_suggester.suggest(brief)
        print("   MVP предложен")
    
        print("6. Написание ответа заказчику...")
        draft = self.response_writer.write(brief, evaluation)
        print("   Ответ готов")

        return AssistantResponse(
            brief_title=brief.title,
            evaluation=evaluation,
            questions=questions,
            mvp=mvp,
            formatted_text=draft,
            generated_at=datetime.now(timezone.utc),
        )

    def run_from_files(self, brief_path: Path, *, tz_path: Path | None = None) -> AssistantResponse:
        brief_text = brief_path.read_text(encoding="utf-8")
        technical_spec = tz_path.read_text(encoding="utf-8") if tz_path else None
        return self.run(brief_text, technical_spec=technical_spec)