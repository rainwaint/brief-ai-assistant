# ИИ-ассистент оценки проектных брифов

Сервис для автоматизированного анализа проектных брифов. Оценивает соответствие требованиям, генерирует уточняющие вопросы, предлагает MVP и формирует черновик ответа заказчику.

## Возможности

- Извлечение структурированных данных из текста брифа
- Оценка по гибким критериям (YAML-конфиг)
- Генерация уточняющих вопросов
- Предложение минимально жизнеспособного продукта (MVP)
- Черновик ответа заказчику
- Работа через YandexGPT (или локальные модели Ollama)

## Технологии

- Python 3.10+
- Pydantic
- LangChain
- YandexGPT / Ollama
- Click (CLI)

## Установка

```bash
git clone https://github.com/rainwaint/brief-ai-assistant.git
cd brief-ai-assistant
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate
pip install -e .
```

## Настройка

Создайте файл `.env`:

```env
YANDEX_API_KEY=ваш_ключ
YANDEX_FOLDER_ID=ваш_folder_id
```

Критерии оценки находятся в `config/criteria.yaml`.

## Запуск

```bash
brief-evaluator evaluate --brief sample_brief.txt --save
```

Результат сохранится в `results/result_*.json`.

## Пример брифа

В файле `sample_brief.txt` приведён пример брифа для тестирования.

## Тесты

```bash
pytest tests/
```

## Структура

```
brief-evaluator/
├── config/
│   └── criteria.yaml
├── src/
│   └── brief_evaluator/
│       ├── extractor/
│       ├── evaluator/
│       ├── question_generator/
│       ├── mvp_suggester/
│       ├── response_writer/
│       ├── llm/
│       ├── models.py
│       ├── pipeline.py
│       ├── cli.py
│       └── config.py
├── tests/
├── pyproject.toml
├── README.md
└── .env.example
```







