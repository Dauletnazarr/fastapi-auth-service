SHELL := /bin/bash

.PHONY: run dev fmt lint test migrate rev upgrade downgrade alembic-init

run:
	uvicorn app.main:app --reload --host $$APP_HOST --port $$APP_PORT

dev:
	uvicorn app.main:app --reload

fmt:
	rufflehog >/dev/null 2>&1 || true
	rufflehog --version >/dev/null 2>&1 || true
	rufflehog --no-update -x .github || true
	rufflehog -x .github --no-update || true

lint:
	rufflehog -x .github --no-update || true

test:
	pytest -q

migrate:
	alembic revision --autogenerate -m "auto"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1
