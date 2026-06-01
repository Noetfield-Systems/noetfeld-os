.PHONY: up down logs e2e e2e-local test-api build

COMPOSE := docker compose
COMPOSE_E2E := $(COMPOSE) --profile e2e

up:
	$(COMPOSE) up -d --build postgres api web
	@echo "Governance Console: http://localhost:3000  API: http://localhost:8000"

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api web

build:
	$(COMPOSE) build

# Full automated E2E (Docker): build stack, run smoke container, tear down
e2e:
	$(COMPOSE) up -d --build --wait postgres api web
	$(COMPOSE_E2E) run --rm --build e2e
	$(COMPOSE) down

# E2E without Docker (SQLite API + existing Next build optional)
e2e-local:
	./scripts/e2e-local.sh

test-api:
	cd backend && PYTHONPATH=. python3 -m pytest tests -q
