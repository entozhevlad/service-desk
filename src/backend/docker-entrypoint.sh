#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  uv run alembic upgrade head
fi

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
