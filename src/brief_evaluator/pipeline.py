"""Main pipeline orchestrating all steps."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from brief_evaluator.models import AssistantResponse
from brief_evaluator.protocols import (
    BriefExtractor,
    BriefEvaluator,
    QuestionGenerator,
    MVPSuggester,
    ResponseWriter,
    CriteriaProvider,
)
from brief_evaluator.logger import save_result


class EvaluationPipeline:
    def __init__(
        self,
        extractor: BriefExtractor,
        evaluator: BriefEvaluator,
        question_generator: QuestionGenerator,
        mvp_suggester: MVPSuggester,
        response_writer: ResponseWriter,
        criteria_provider: CriteriaProvider,
        retriever=None,
        use_rag: bool = False,
        rag_folder: str = "data/projects_examples",
    ) -> None:
        self.extractor = extractor
        self.evaluator = evaluator
        self.question_generator = question_generator
        self.mvp_suggester = mvp_suggester
        self.response_writer = response_writer
        self.criteria_provider = criteria_provider
        self.retriever = retriever
        self.use_rag = use_rag
        self.rag_folder = rag_folder

        # Если RAG включён, но ретривер не передан — создаём свой
        if use_rag and retriever is None:
            from brief_evaluator.rag.bert_retriever import BertRetriever
            self.retriever = BertRetriever()
            self.retriever.add_folder(rag_folder)
            print(f"✅ RAG инициализирован, папка: {rag_folder}")

    def run(self, raw_text: str, *, technical_spec: str | None = None) -> AssistantResponse:
        print("📋 1/7 Загрузка критериев...")
        criteria = self.criteria_provider.load()
        print("   ✅ Критерии загружены")

        # RAG-поиск
        if self.use_rag and self.retriever:
            print("🔍 2/7 Поиск похожих проектов (RAG)...")
            similar_projects = self.retriever.search(raw_text, top_k=2)
            print(f"   ✅ Найдено проектов: {len(similar_projects)}")
        else:
            print("⏭️  RAG отключён")

        print("📂 3/7 Извлечение данных из брифа...")
        brief = self.extractor.extract(raw_text, technical_spec=technical_spec)
        print(f"   ✅ Извлечено: {brief.title}")

        print("📊 4/7 Оценка по критериям...")
        evaluation = self.evaluator.evaluate(brief, criteria)
        print(f"   ✅ Оценка: {evaluation.overall_score:.2f} (пройдено: {evaluation.passed})")

        print("❓ 5/7 Генерация уточняющих вопросов...")
        questions = self.question_generator.generate(brief)
        print(f"   ✅ Вопросов: {len(questions)}")

        print("🚀 6/7 Предложение MVP...")
        mvp = self.mvp_suggester.suggest(brief)
        print(f"   ✅ MVP: {mvp.title}")

        print("✉️ 7/7 Написание ответа заказчику...")
        draft = self.response_writer.write(brief, evaluation)
        print("   ✅ Ответ готов")

        print("📦 Формирование итогового результата...")
        result = AssistantResponse(
            brief_title=brief.title,
            evaluation=evaluation,
            questions=questions,
            mvp=mvp,
            formatted_text=draft,
            generated_at=datetime.now(timezone.utc),
        )
        print("   ✅ Результат сформирован")

        try:
            save_result(result, raw_text)
            print("   💾 Результат сохранён в папку results/")
        except Exception as e:
            print(f"   ⚠️ Не удалось сохранить результат: {e}")

        return result

    def run_from_files(self, brief_path: Path, *, tz_path: Path | None = None) -> AssistantResponse:
        print(f"📁 Загрузка брифа из файла: {brief_path}")
        brief_text = brief_path.read_text(encoding="utf-8")
        technical_spec = tz_path.read_text(encoding="utf-8") if tz_path else None
        return self.run(brief_text, technical_spec=technical_spec)