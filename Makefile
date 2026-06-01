.PHONY: bootstrap validate api api-v3 apply-migrations ingest-sot-dry-run ingest-sot phase32-smoke phase32-postgres-smoke phase33-verify phase33-postgres-verify phase35-demo final-lock-audit final-lock-semantic governance-console-up governance-console-e2e governance-console-down

PYTHONPATH_VALUE := packages/types:packages/config:packages/sdk:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance

bootstrap:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip
	. .venv/bin/activate && python -m pip install -e ".[dev]"
	npm install

validate:
	python3 -m compileall packages services
	git diff --check

api:
	PYTHONPATH=$(PYTHONPATH_VALUE) uvicorn noetfield_governance.api:app --reload --app-dir services/governance

api-v3:
	PYTHONPATH=$(PYTHONPATH_VALUE) uvicorn noetfield_governance.api:app --reload --host 0.0.0.0 --port 8001 --app-dir services/governance

apply-migrations:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/apply_postgres_migrations.py

ingest-sot-dry-run:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/ingest_source_inventory.py --dry-run

ingest-sot:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/ingest_source_inventory.py

phase32-smoke:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 scripts/phase_3_2_backend_smoke.py

phase32-postgres-smoke:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=postgres python3 scripts/phase_3_2_backend_smoke.py --postgres

phase33-verify:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m pytest tests/unit

phase33-postgres-verify:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=postgres pytest tests/integration


phase35-demo:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 scripts/run_copilot_governance_demo.py --input demos/copilot-governance/sample_copilot_signal.json --output demos/copilot-governance/generated/demo_output.json

final-lock-semantic:
	python3 scripts/final_semantic_lock_public.py

final-lock-audit:
	python3 scripts/audit_final_system_lock.py

verify-final-lock: final-lock-audit
	python3 scripts/audit_intake_email.py
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m pytest tests/unit -q

console-smoke:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m pytest tests/unit/test_governance_console_v3.py -q

site-health:
	python3 scripts/audit_public_site_health.py
	python3 scripts/audit_no_secrets_in_repo.py
	python3 scripts/smoke_bank_grade_html.py
	python3 -m pytest tests/unit/test_public_gtm_alignment.py tests/unit/test_public_simplification.py -q

sitemap:
	python3 scripts/generate_sitemap.py

trust-brief-export:
	chmod +x scripts/trust_brief_audit_export.sh
	@test -n "$(RID)" || (echo "Usage: make trust-brief-export RID=RID-..." && exit 1)
	./scripts/trust_brief_audit_export.sh --request-id "$(RID)" --out ./exports

generate-openapi:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/generate_public_openapi.py

seed-msb-pack:
	./scripts/seed-msb-partner-pack.sh

go-live-check:
	@echo "See docs/GO_LIVE.md — run deploy_platform_smoke.sh against production when DNS is ready."

ecosystem-health:
	python3 scripts/audit_no_secrets_in_repo.py
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m pytest tests/unit/test_public_chat.py tests/unit/test_openrouter_client.py tests/unit/test_telegram_webhook.py tests/unit/test_public_intake.py tests/unit/test_practical_ecosystem.py tests/unit/test_chat_quality.py -q

verify-platform-health:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/verify_platform_health.py

platform-up:
	docker compose -f infrastructure/docker/docker-compose.yml -f infrastructure/docker/docker-compose.platform.yml up -d --build

platform-migrate:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/apply_postgres_migrations.py

platform-sync-knowledge:
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 scripts/sync_knowledge_chunks.py

collapse-public:
	python3 scripts/collapse_public_routes.py

governance-console-up:
	cd governance-console && ./scripts/up.sh

governance-console-e2e:
	cd governance-console && make e2e

governance-console-down:
	cd governance-console && make down
