SHELL := /bin/bash

ENV_FILE ?= .env.local

.PHONY: run-service

run-service:
	set -a; [ -f $(ENV_FILE) ] && source $(ENV_FILE); set +a; \
	cd src/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $${BACKEND_PORT:-8000}
