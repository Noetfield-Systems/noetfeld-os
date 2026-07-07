.PHONY: test gate demo build-gate-js install inbox cloud-worker autorun-once autorun autorun-status autorun-tick-deploy autorun-tick-dispatch autonomous-verify schedule-verify determinism-verify replay-verify planes supabase-migrate verified-window loop-run loop-fleet-deploy deploy-railway-loop-runner verify-cf-railway-dispatch loop-fleet-dispatch loops-status loop-heartbeat loop-baseline loop-registry-reconcile loop-verify-all loop-upgrade-closeout trigger-host-inventory deadman-deploy deadman-probe cloud-motor-e2e cloud-motor-resync deploy-baseline deploy-status deploy-fly-inbox deploy-fly-selfheal deploy-drift-kaizen inbox-scaler inbox-scaler-evaluate sandbox-registry-reconcile improve-kaizen-daily t2-deploy-closeout t3-sandbox-closeout acg-founder-send-prep backlog urls local-boot local-closeout local-patch-proposal local-heartbeat local-lane local-sweep-stale local-status machine-status machine-reconcile machine-audit machine-verify machine-validate-merge machine-critic machine-research

test:
	pytest -q

gate:
	noetfield gate

demo:
	bash scripts/demo-gel-5min-v1.sh

install:
	pip install -e .

build-gate-js:
	cd packages/gate && npm install && npm run build

inbox:
	python3 scripts/enqueue_noos_cloud_inbox_v1.py

cloud-worker:
	python3 scripts/cloud_inbox_worker_v1.py

autorun-once:
	python3 scripts/run_noetfield_factory_loop_v1.py --once

autorun:
	python3 scripts/run_noetfield_factory_loop_v1.py --interval-seconds 600

autorun-status:
	python3 scripts/autorun_status_v1.py

autorun-tick-deploy:
	bash scripts/deploy_noos_factory_autorun_tick_cf_v1.sh

autorun-tick-dispatch:
	python3 scripts/trigger_noos_factory_dispatch_v1.py

autonomous-verify:
	python3 scripts/verify_noos_autonomous_24h_v1.py --write-receipt --json

schedule-verify:
	python3 scripts/verify_noos_github_schedule_v1.py --write-receipt --json

determinism-verify:
	python3 scripts/verify_loop_determinism_external_v1.py --write-receipt --json

replay-verify:
	python3 scripts/verify_noos_loop_replay_v1.py --write-receipt --json

planes:
	python3 scripts/planes_status_v1.py --json

supabase-migrate:
	@test -n "$(MIGRATION)" || (echo "Usage: make supabase-migrate MIGRATION=0012" && exit 1)
	python3 scripts/apply_supabase_migration_v1.py --migration $(MIGRATION) --write-receipt --json

verified-window:
	python3 scripts/open_noos_verified_window_v1.py --write-receipt --json

loop-run:
	@test -n "$(EVENT)" || (echo "Usage: make loop-run EVENT=noos_chain_loop_tick" && exit 1)
	python3 scripts/noos_loop_runner_v1.py --event-type $(EVENT) --json

loop-fleet-deploy:
	bash scripts/deploy_noos_loop_fleet_tick_cf_v1.sh

deploy-railway-loop-runner:
	bash scripts/deploy_noos_loop_runner_railway_v1.sh

verify-cf-railway-dispatch:
	python3 scripts/verify_noos_cf_railway_dispatch_v1.py --write-receipt --json

loop-fleet-dispatch:
	python3 scripts/trigger_noos_loop_dispatch_v1.py --all --json

loops-status:
	@python3 -c "import json; d=json.load(open('data/noos-24-7-loops-v1.json')); print(json.dumps({'motor':d['motor'],'loops':[{'id':x['id'],'interval':x['interval_minutes'],'event':x['event_type']} for x in d['loops']]}, indent=2))"

loop-heartbeat:
	python3 scripts/noos_loop_heartbeat_v1.py --write-receipt --json

loop-baseline:
	python3 scripts/noos_loop_baseline_audit_v1.py --write-receipt --json

loop-registry-reconcile:
	python3 scripts/noos_loop_registry_reconcile_v1.py --write-receipt --json

trigger-host-inventory:
	python3 scripts/noos_trigger_host_inventory_v1.py --write-data --write-receipt --json

deadman-deploy:
	bash scripts/deploy_noos_deadman_cf_v1.sh

deadman-probe:
	curl -fsS -X POST "https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/check?telegram=0" | python3 -m json.tool

deadman-telegram-verify:
	python3 scripts/verify_noos_deadman_telegram_lane_v1.py --fail-on-forbidden --json

deadman-telegram-test:
	@echo "Founder-only: sends ONE test alert if lane valid and send_alerts=true in config"
	curl -fsS -X POST "https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/check?telegram=1" | python3 -m json.tool

cloud-motor-e2e:
	bash scripts/verify_noos_cloud_motor_e2e_v1.sh

cloud-motor-resync:
	bash scripts/phase_b_wire_cf_railway_motor_v1.sh

cloud-secrets-sync:
	bash scripts/noos_sync_cloud_secrets_v1.sh

cloud-workers-deploy:
	gh workflow run deploy-noos-cloud-workers-v1.yml --repo Noetfield-Systems/noetfeld-os

integrator-repair-autorun:
	python3 scripts/noos_integrator_repair_autorun_v1.py --write-receipt --json

cloud-vault-promote:
	python3 scripts/noos_promote_vault_keys_v1.py

cloud-vault-canonicalize:
	python3 scripts/canonicalize_noos_vault_v1.py

cloud-vault-cleanup:
	python3 scripts/cleanup_noetfield_vault_v1.py

cloud-vault-migrate:
	bash scripts/migrate_noos_vault_from_sourcea_v1.sh

wire-cf-railway-motor:
	bash scripts/phase_b_wire_cf_railway_motor_v1.sh

wire-cf-fly-motor:
	@echo "DEPRECATED: Fly executor destroyed; use wire-cf-railway-motor"
	bash scripts/phase_b_wire_cf_railway_motor_v1.sh

motor-restart:
	python3 scripts/noos_motor_restart_v1.py --recipe $(RECIPE) --write-receipt --json

motor-status:
	python3 scripts/noos_motor_restart_v1.py --recipe cf-loop-motor --dry-run --json && \
	python3 scripts/noos_motor_restart_v1.py --recipe cf-deadman --dry-run --json && \
	python3 scripts/noos_motor_restart_v1.py --recipe railway-loop-runner --dry-run --json

living-system-baseline:
	python3 scripts/verify_noos_living_system_48h_v1.py --baseline --write-receipt --json

living-system-verify-48h:
	python3 scripts/verify_noos_living_system_48h_v1.py --final --write-receipt --json

seed-loop-liveness:
	python3 scripts/seed_noos_loop_liveness_v1.py --tick-all --json

cloud-motor-ops-receipt:
	python3 scripts/write_noos_cloud_motor_ops_receipt_v1.py

loop-verify-all:
	python3 scripts/noos_loop_verify_v1.py --json all --write-receipt --lookback-hours 24 --fallback-hours 168

loop-upgrade-closeout:
	python3 scripts/noos_loop_upgrade_closeout_v1.py --json --write-receipt

deploy-baseline:
	python3 scripts/noos_deploy_baseline_audit_v1.py --write-receipt --json

deploy-status:
	python3 scripts/noetfield_deploy_v1.py status --json

deploy-fly-inbox:
	python3 scripts/noetfield_deploy_v1.py deploy --scope fly-inbox --write-receipt --json

deploy-fly-selfheal:
	python3 scripts/noetfield_deploy_v1.py deploy --scope fly-self-heal --write-receipt --json

deploy-fly-loop-executor:
	bash scripts/deploy_noos_loop_executor_fly_v1.sh

verify-fly-loop-executor:
	python3 scripts/verify_noos_loop_executor_fly_v1.py --write-receipt --json

verify-railway-loop-runner:
	python3 scripts/verify_noos_loop_runner_railway_v1.py --write-receipt --json

deploy-drift-kaizen:
	python3 scripts/noos_deploy_drift_kaizen_v1.py --inject-drift --write-receipt --json

inbox-scaler:
	python3 scripts/noos_inbox_scaler_v1.py --simulate-pending 11 --write-receipt --json

inbox-scaler-evaluate:
	python3 scripts/noos_inbox_scaler_v1.py --evaluate-all --write-receipt --json

sandbox-registry-reconcile:
	python3 scripts/noos_sandbox_registry_reconcile_v1.py --write-receipt --json

improve-kaizen-daily:
	python3 scripts/noos_improve_kaizen_runner_v1.py --write-receipt --json

t2-deploy-closeout:
	python3 scripts/noos_t2_deploy_closeout_v1.py --write-receipt --json

t3-sandbox-closeout:
	python3 scripts/noos_t3_sandbox_closeout_v1.py --write-receipt --json

acg-founder-send-prep:
	python3 scripts/noos_acg_founder_send_prep_v1.py --write-receipt --json

backlog:
	@python3 -c "import json; d=json.load(open('data/noos-unified-upgrade-backlog-v1.json')); print(json.dumps({'tiers':d['tier_definitions'],'summary':d['summary'],'next':[x['id'] for x in d['items'] if x.get('tier')=='T1' and x.get('status')=='open']}, indent=2))"

urls:
	bash scripts/check_production_urls.sh

local-boot:
	git status --short
	git branch --show-current
	bash scripts/noos_local_boot_vault_sync_v1.sh
	python3 scripts/noos_integrator_sync_v1.py init
	python3 scripts/noos_integrator_sync_v1.py register-agent \
	  --agent-id cursor-local-mac --ide cursor --role local-operator
	python3 scripts/noos_integrator_sync_v1.py register-agent \
	  --agent-id copilot-cli-mac --ide copilot-cli --role local-operator
	python3 scripts/noos_integrator_sync_v1.py sweep-stale
	python3 scripts/noos_agent_conflict_check_v1.py --json
	python3 scripts/verify_living_system_governance_v1.py --json
	python3 scripts/noos_integrator_sync_v1.py summary --json
	python3 scripts/noos_integrator_mirror_check_v1.py --json
	@if [ "$(WRITE_RECEIPT)" = "1" ]; then python3 scripts/noos_local_boot_receipt_v1.py --json; fi

local-lane:
	@test -n "$(TASK)" || (echo "Usage: make local-lane TASK=NOOS-LANE-001 SCOPE=path1,path2" && exit 1)
	@test -n "$(SCOPE)" || (echo "Usage: make local-lane TASK=NOOS-LANE-001 SCOPE=path1,path2" && exit 1)
	$(MAKE) local-boot
	bash scripts/noos_local_claim_lane_v1.sh $(TASK) $$(echo "$(SCOPE)" | tr ',' ' ')

local-sweep-stale:
	python3 scripts/noos_integrator_sync_v1.py sweep-stale

local-status:
	python3 scripts/noos_local_status_v1.py

local-heartbeat:
	@test -n "$(TASK)" || (echo "Usage: make local-heartbeat TASK=NOOS-LANE-001 [AGENT_ID=cursor-local-mac IDE=cursor]" && exit 1)
	python3 scripts/noos_integrator_sync_v1.py heartbeat \
	  --agent-id $${AGENT_ID:-cursor-local-mac} --ide $${IDE:-cursor} --task-id $(TASK)

local-closeout:
	@test -n "$(TASK)" || (echo "Usage: make local-closeout TASK=NOOS-LANE-001 [AGENT_ID=... IDE=...]" && exit 1)
	python3 -m pytest -q || ($(MAKE) local-sweep-stale; exit 1)
	bash scripts/check_noos_clean_tree.sh || ($(MAKE) local-sweep-stale; exit 1)
	python3 scripts/noos_integrator_sync_v1.py complete \
	  --agent-id $${AGENT_ID:-cursor-local-mac} --ide $${IDE:-cursor} \
	  --task-id $(TASK) --note "lane closed"
	@if [ "$(WRITE_RECEIPT)" = "1" ]; then \
		AGENT_ID=$${AGENT_ID:-cursor-local-mac} IDE=$${IDE:-cursor} \
		python3 scripts/noos_local_closeout_receipt_v1.py \
		  --task-id $(TASK) --agent-id $${AGENT_ID} --ide $${IDE} \
		  --pytest-ok true --clean-tree-ok true --complete-ok true --json; \
	fi

local-patch-proposal:
	@if [ -n "$(PAYLOAD_FILE)" ]; then \
		python3 scripts/noos_worker_kernel_v1.py --task-kind patch_proposal --payload-file "$(PAYLOAD_FILE)" --json; \
	elif [ -n "$(PATHS)" ]; then \
		python3 scripts/noos_worker_kernel_v1.py --task-kind patch_proposal --payload "$$(python3 -c "import json,os; paths=[p.strip() for p in os.environ.get('PATHS','').split(',') if p.strip()]; print(json.dumps({'files':[{'path':p,'content':''} for p in paths]}))")" --json; \
	else \
		echo "Usage: make local-patch-proposal PAYLOAD_FILE=proposal.json"; \
		echo "   or: make local-patch-proposal PATHS=scripts/foo.py,tests/test_foo.py"; \
		exit 1; \
	fi

machine-status:
	python3 scripts/noos_machine_loops_v1.py status

machine-reconcile:
	python3 scripts/noos_machine_loops_v1.py reconcile

machine-audit:
	python3 scripts/noos_machine_loops_v1.py audit

machine-verify:
	python3 scripts/noos_machine_loops_v1.py verify

machine-validate-merge:
	python3 scripts/noos_machine_loops_v1.py validate-merge

machine-critic:
	@test -n "$(RECEIPT)" || (echo "Usage: make machine-critic RECEIPT=receipts/proof/foo.json" && exit 1)
	python3 scripts/noos_machine_loops_v1.py critic --receipt $(RECEIPT)

machine-research:
	@test -n "$(QUESTION)" || (echo "Usage: make machine-research QUESTION='...' [RECEIPT=...]" && exit 1)
	@if [ -n "$(RECEIPT)" ]; then \
		python3 scripts/noos_machine_loops_v1.py research-memo --question "$(QUESTION)" --receipt "$(RECEIPT)"; \
	else \
		python3 scripts/noos_machine_loops_v1.py research-memo --question "$(QUESTION)"; \
	fi
