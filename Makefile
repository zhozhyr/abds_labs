.PHONY: run rund services stop clean gen load setup teardown lint test check
.DEFAULT_GOAL = run

COMPOSE = docker compose --env-file .env.local

# Runs all services in detached mode.
run:
	$(COMPOSE) up -d --build

# Runs all services without detached mode (for debugging).
rund:
	$(COMPOSE) up --build

# Shows all service statuses.
services:
	$(COMPOSE) ps

# Stops all running services.
stop:
	$(COMPOSE) down

# Cleans up all resources including volumes.
clean:
	$(COMPOSE) down

gen:
	poetry run python -m scripts.generate

load:
	./scripts/load.sh

setup:
	./scripts/setup.sh

teardown:
	./scripts/teardown.sh

lint:
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run mypy app scripts tests

test:
	poetry run pytest

check: lint test
