.PHONY: bootstrap validate api api-v3 apply-migrations ingest-sot-dry-run ingest-sot phase32-smoke phase32-postgres-smoke phase33-verify phase33-postgres-verify phase35-demo final-lock-audit final-lock-semantic verify-investor-lane verify-commercial-agentic verify-law-stack sync-derived-docs verify-factory-copilot verify-factory-catalog

PYTHONPATH_VALUE := packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance:services/factories

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
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory pytest tests/unit

phase33-postgres-verify:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=postgres pytest tests/integration


phase35-demo:
	PYTHONPATH=$(PYTHONPATH_VALUE) RUNTIME_EVENT_STORE=memory python3 scripts/run_copilot_governance_demo.py --input demos/copilot-governance/sample_copilot_signal.json --output demos/copilot-governance/generated/demo_output.json

final-lock-semantic:
	python3 scripts/final_semantic_lock_public.py

final-lock-audit:
	python3 scripts/audit_final_system_lock.py

verify-final-lock: final-lock-audit
	pytest tests/unit/test_public_gtm_alignment.py tests/unit/test_golden_edge_v3.py -q

verify-investor-lane:
	./scripts/verify-investor-diligence-lane.sh
	python3 -m pytest tests/unit/test_investor_diligence_lane.py -q

verify-commercial-agentic:
	chmod +x ./scripts/verify-commercial-agentic.sh
	./scripts/verify-commercial-agentic.sh
	python3 -m pytest tests/unit/test_commercial_agentic.py -q

sync-derived-docs:
	chmod +x ./scripts/sync-derived-docs.sh
	./scripts/sync-derived-docs.sh

verify-law-stack:
	chmod +x ./scripts/verify-law-stack.sh
	./scripts/verify-law-stack.sh
	python3 -m pytest tests/unit/test_law_stack.py -q

verify-factory-copilot:
	chmod +x ./scripts/verify-factory-copilot.sh
	./scripts/verify-factory-copilot.sh
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 -m pytest tests/unit/test_factory_copilot.py -q

verify-factory-catalog:
	chmod +x ./scripts/verify-factory-catalog.sh
	./scripts/verify-factory-catalog.sh
	PYTHONPATH=$(PYTHONPATH_VALUE) python3 -m pytest tests/unit/test_factory_catalog.py -q
