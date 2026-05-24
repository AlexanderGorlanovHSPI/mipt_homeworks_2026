# Описание проекта

Консольный ИИ-ассистент для общения с LLM через OpenAI-compatible API.

## Что умеет

- чатиться с LLM;
- хранить историю сообщений;
- ограничивать контекст по числу сообщений и символов;
- читать настройки из `.env`, переменных окружения и `config.yaml`;
- прикреплять текстовые файлы через `@::path::`;
- обрабатывать файл по частям через `/filechunk`;
- очищать историю через `/reset`;
- выходить по `\q`.

## Установка

```bash
cd final_project
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Для проверок:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
```

## Конфигурация

Можно использовать `.env`:

```bash
cp .env.example .env
```

Пример:

```env
API_KEY=ollama
API_HOST=http://localhost:11434/v1/
MODEL=gemma3:270m
LIMIT_MESSAGE=20
LIMIT_CHARS=2000
TEMPERATURE=0.5
```

Также можно использовать `config.yaml`. Переменные окружения и `.env` имеют
приоритет над `config.yaml`.

`system_prompt` задается в `config.yaml`.

## Запуск

```bash
.venv/bin/python main.py
```

## Команды

```text
\q
```

Выйти из программы.

```text
/reset
```

Очистить историю чата и экран.

```text
@::/path/to/file.py::
```

Подставить содержимое текстового файла в сообщение. Максимальный размер файла:
`5 MB`.

```text
/filechunk
/filechunk paragraph=3
/filechunk len=150
/filechunk paragraph=3 -y
```

Обработать файл по частям. Флаг `-y` запускает обработку всех чанков подряд.

## Проверки

```bash
.venv/bin/ruff check --config ruff.toml .
.venv/bin/mypy .
```
