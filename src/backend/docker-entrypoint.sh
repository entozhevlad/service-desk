#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  uv run alembic upgrade head
fi

UVICORN_ARGS="--host 0.0.0.0 --port 8000"
if [ "${UVICORN_RELOAD:-0}" = "1" ]; then
  UVICORN_ARGS="$UVICORN_ARGS --reload"
fi

exec uv run uvicorn app.main:app $UVICORN_ARGS
