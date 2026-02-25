# Contributing (Backend)

## Как получить проект
```bash
git clone https://github.com/entozhevlad/service-desk.git
cd service-desk
```

## Установить uv
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

## Установить зависимости
```bash
cd src/backend
uv sync
```

## Поднять БД в Docker
```bash
docker compose --env-file .env.local up -d db
```

## Миграции
```bash
cd src/backend
set -a; [ -f ../.env.local ] && source ../.env.local; set +a
uv run alembic upgrade head
```

## Запуск локально
```bash
cd src/backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Тесты
```bash
cd src/backend
uv run pytest
```

## Линтеры
```bash
cd src/backend
uv run isort --check-only app
uv run flake8 app
uv run mypy app
```

## Запуск в Docker
```bash
docker compose --env-file .env.local up -d --build
```
