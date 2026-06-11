.PHONY: bootstrap validate api api-v3 apply-migrations ingest-sot-dry-run ingest-sot phase32-smoke phase32-postgres-smoke phase33-verify phase33-postgres-verify phase35-demo final-lock-audit final-lock-semantic governance-console-up governance-console-e2e governance-console-down plan-with-no-asf-verify sync-prompt-pack generate-prompt-pack

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
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m uvicorn noetfield_governance.api:app --reload --host 0.0.0.0 --port 8000 --app-dir services/governance

api-v3:
	@. ./scripts/dev-ports.sh && PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 -m uvicorn noetfield_governance.api:app --reload --host 0.0.0.0 --port $$PLATFORM_CONSOLE_PORT --app-dir services/governance

platform-console-dev:
	@chmod +x scripts/dev-platform-console.sh
	./scripts/dev-platform-console.sh

platform-console-up:
	@chmod +x scripts/ensure-platform-console.sh
	./scripts/ensure-platform-console.sh

platform-console-down:
	@if [ -f .platform-console.pid ]; then kill $$(cat .platform-console.pid) 2>/dev/null || true; rm -f .platform-console.pid; fi
	@. ./scripts/dev-ports.sh && lsof -tiTCP:$$PLATFORM_CONSOLE_PORT -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true

dev-local:
	@chmod +x scripts/dev-local-all.sh scripts/verify-local-dev.sh scripts/dev-local-down.sh
	./scripts/dev-local-all.sh

# Pro mode: production Next build + no API hot-reload (lower CPU/RAM than next dev)
dev-local-pro:
	@chmod +x scripts/dev-local-all.sh scripts/dev-local-down.sh scripts/dev-platform-console.sh
	NF_DASHBOARD_MODE=production NF_DEV_HOT_RELOAD=0 ./scripts/dev-local-all.sh

dev-local-down:
	@chmod +x scripts/dev-local-down.sh
	./scripts/dev-local-down.sh

verify-local-dev:
	@chmod +x scripts/verify-local-dev.sh
	./scripts/verify-local-dev.sh

verify-agent-scope:
	@chmod +x scripts/verify-agent-scope.sh
	./scripts/verify-agent-scope.sh

verify-ui-e2e:
	@chmod +x scripts/verify-ui-e2e.sh
	./scripts/verify-ui-e2e.sh

plan-with-no-asf-verify:
	@chmod +x scripts/plan-with-no-asf-verify.sh scripts/verify-copilot-demo-links.sh
	./scripts/plan-with-no-asf-verify.sh

sync-prompt-pack:
	@python3 scripts/sync-prompt-pack-status.py

generate-prompt-pack:
	@python3 scripts/generate-prompt-pack-v2.py
	@python3 scripts/sync-prompt-pack-status.py

plans-regen:
	@python3 scripts/generate-plans-registry.py

plans-done:
	@echo "Usage: python3 scripts/update-plan-status.py NF-PLAN-0001 --status done"

demo-url:
	@chmod +x scripts/print-demo-url.sh
	./scripts/print-demo-url.sh

procurement-pack-e2e:
	@chmod +x scripts/procurement-pack-e2e.sh
	./scripts/procurement-pack-e2e.sh

# Pre-demo GTM bundle (Mac waves 034–042)
verify-gtm:
	@chmod +x scripts/verify-gtm.sh
	./scripts/verify-gtm.sh

# Merge/deploy readiness (cloud canonical — superset of verify-gtm checks)
generate-noetfield-1000:
	@chmod +x scripts/generate-noetfield-1000-prompts.py
	python3 scripts/generate-noetfield-1000-prompts.py

agent-session-start:
	@chmod +x scripts/agent-session-start.sh
	./scripts/agent-session-start.sh

ingest-cursor-reply:
	@chmod +x scripts/ingest-cursor-reply.sh
	./scripts/ingest-cursor-reply.sh

sync-sourceA:
	@chmod +x scripts/sync-sourceA-desktop.sh
	./scripts/sync-sourceA-desktop.sh

ship-closeout:
	@chmod +x scripts/ship-closeout.sh
	./scripts/ship-closeout.sh

agent-session-close:
	@chmod +x scripts/agent-session-close.sh
	./scripts/agent-session-close.sh

smoke-pick-no-asf-plan:
	@chmod +x scripts/smoke-pick-no-asf-plan.sh
	./scripts/smoke-pick-no-asf-plan.sh

verify-lane-fences:
	@chmod +x scripts/verify-lane-fences.sh
	./scripts/verify-lane-fences.sh

mirror-noetfield-os-readme:
	@chmod +x scripts/mirror-noetfield-os-readme.py
	python3 scripts/mirror-noetfield-os-readme.py

pick-no-asf-plan:
	@chmod +x scripts/pick-noetfield-no-asf-plan.py
	python3 scripts/pick-noetfield-no-asf-plan.py --tier T0 --limit 1 --prompt

validate-noetfield-1000:
	@chmod +x scripts/validate-noetfield-1000-sources.py
	python3 scripts/validate-noetfield-1000-sources.py

sync-noetfield-plans-status:
	@chmod +x scripts/sync-noetfield-plans-status.py
	python3 scripts/sync-noetfield-plans-status.py

ship-verify:
	@echo "=== ship-verify (Noetfield merge/deploy readiness) ==="
	@chmod +x scripts/verify-agent-scope.sh 2>/dev/null || true
	@./scripts/verify-agent-scope.sh
	@test -f docs/SHIP_NOW.md
	@test -f docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md
	@test -f docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md
	@ls docs/spec/examples/tle-v1-*.yaml | wc -l | grep -q 3
	@chmod +x scripts/tle-smoke.sh scripts/verify-local-dev.sh scripts/smoke_bank_grade_html.py 2>/dev/null || true
	@./scripts/tle-smoke.sh
	@./scripts/verify-local-dev.sh
	@chmod +x scripts/verify-ui-endpoints.sh scripts/verify-docs-diligence.sh 2>/dev/null || true
	@./scripts/verify-ui-endpoints.sh
	@./scripts/verify-docs-diligence.sh
	@./scripts/verify-msb-partner-openapi.sh
	@./scripts/verify-observability-migration.sh
	@chmod +x scripts/verify-tle-performance.sh scripts/verify-workspace-ui-auth.sh 2>/dev/null || true
	@./scripts/verify-tle-performance.sh
	@./scripts/verify-workspace-ui-auth.sh
	@python3 scripts/smoke_bank_grade_html.py
	@python3 scripts/verify_sitemap_committed.py 2>/dev/null || true
	@python3 -m compileall -q packages services 2>/dev/null || true
	@echo "ship-verify: OK"

tle-smoke:
	@chmod +x scripts/tle-smoke.sh scripts/seed-m365-evidence-stub.sh
	./scripts/tle-smoke.sh

copilot-pilot-e2e:
	@chmod +x scripts/copilot-pilot-e2e.sh scripts/seed-m365-evidence-stub.sh
	./scripts/copilot-pilot-e2e.sh

staging-smoke:
	@chmod +x scripts/staging-smoke.sh
	./scripts/staging-smoke.sh

seed-m365-evidence:
	@chmod +x scripts/seed-m365-evidence-stub.sh
	./scripts/seed-m365-evidence-stub.sh

validate-compliance-schemas:
	@chmod +x scripts/validate-compliance-schemas.sh
	./scripts/validate-compliance-schemas.sh

validate-tle-schemas:
	@chmod +x scripts/validate-tle-schemas.sh
	./scripts/validate-tle-schemas.sh

copilot-quickscan-e2e:
	@chmod +x scripts/copilot-quickscan-e2e.sh
	./scripts/copilot-quickscan-e2e.sh

dev-local-tunnel:
	@chmod +x scripts/dev-local-tunnel.sh
	./scripts/dev-local-tunnel.sh

dev-local-status:
	@chmod +x scripts/dev-local-status.sh scripts/dev-kill-port.sh
	./scripts/dev-local-status.sh

dev-local-tunnel-bg:
	@chmod +x scripts/dev-local-tunnel-bg.sh
	NF_DEV_AUTO_TUNNEL=1 ./scripts/dev-local-tunnel-bg.sh

www-dev:
	@echo "Use: make dev-local  (www is http://localhost:13080/)"

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

cognitive-dashboard-dev:
	chmod +x scripts/dev-cognitive-dashboard.sh
	./scripts/dev-cognitive-dashboard.sh
