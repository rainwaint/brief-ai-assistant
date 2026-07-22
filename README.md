# ИИ-ассистент оценки проектных брифов

Сервис для автоматизированного анализа проектных брифов. Оценивает соответствие требованиям, генерирует уточняющие вопросы, предлагает MVP и формирует черновик ответа заказчику.

## Возможности

- **Извлечение структурированных данных** из текста брифа (название, цель, задачи, направление, материалы, риски)
- **Оценка по гибким критериям** (YAML-конфиг, легко меняется без кода)
- **Генерация уточняющих вопросов** к заказчику
- **Предложение минимально жизнеспособного продукта (MVP)**
- **Формирование черновика ответа** заказчику
- **RAG-поиск** похожих проектов через BERT
- **Веб-интерфейс** на Streamlit
- **CLI** для запуска из командной строки

## Технологии

- Python 3.10+
- Pydantic
- LangChain
- YandexGPT (OpenAI-совместимый API)
- BERT (sentence-transformers)
- Click (CLI)
- Streamlit (веб-интерфейс)
- PyYAML (конфигурация)

##  Установка

```bash
# Клонировать репозиторий
git clone https://github.com/rainwaint/brief-ai-assistant.git
cd brief-ai-assistant

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate      # Windows

# Установить проект
pip install -e .
```

## Настройка

Создайте файл `.env` в корне проекта:

```env
YANDEX_API_KEY=ваш_ключ
YANDEX_FOLDER_ID=ваш_folder_id
```

Критерии оценки находятся в `config/criteria.yaml` — их можно редактировать без изменения кода.

## Запуск через CLI

```bash
# Базовый запуск
brief-evaluator evaluate --brief sample_brief.txt

# С сохранением результата в JSON
brief-evaluator evaluate --brief sample_brief.txt --save

# С RAG-поиском похожих проектов
brief-evaluator evaluate --brief sample_brief.txt --save --rag
```

Результат сохраняется в `results/result_*.json`.

## Веб-интерфейс (Streamlit)

```bash
streamlit run app.py
```

Откроется браузер с интерфейсом для загрузки брифа и просмотра результата.

## Стуктура проекта

```
brief-evaluator/
├── config/
│   └── criteria.yaml          # Критерии оценки
├── data/
│   └── projects_examples/     # Примеры проектов для RAG
├── src/
│   └── brief_evaluator/
│       ├── extractor/         # Извлечение данных
│       ├── evaluator/         # Оценка по критериям
│       ├── question_generator/ # Генерация вопросов
│       ├── mvp_suggester/      # Предложение MVP
│       ├── response_writer/    # Черновик ответа
│       ├── rag/                # RAG (BERT-поиск)
│       ├── llm/                # Клиенты для LLM (YandexGPT, Ollama)
│       ├── models.py           # Pydantic-модели
│       ├── pipeline.py         # Основной пайплайн
│       ├── cli.py              # CLI
│       └── logger.py           # Логирование и сохранение
├── tests/                      # Тесты
├── app.py                      # Streamlit-приложение
├── pyproject.toml
├── README.md
└── .env.example
```

## Тесты

```bash
pytest tests/
```





