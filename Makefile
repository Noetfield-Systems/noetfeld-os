.PHONY: test gate demo build-gate-js install inbox cloud-worker autorun-once autorun autorun-status autorun-tick-deploy autorun-tick-dispatch autonomous-verify schedule-verify determinism-verify planes supabase-migrate verified-window loop-run loop-fleet-deploy loop-fleet-dispatch loops-status loop-heartbeat backlog urls

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

loop-fleet-dispatch:
	python3 scripts/trigger_noos_loop_dispatch_v1.py --all --json

loops-status:
	@python3 -c "import json; d=json.load(open('data/noos-24-7-loops-v1.json')); print(json.dumps({'motor':d['motor'],'loops':[{'id':x['id'],'interval':x['interval_minutes'],'event':x['event_type']} for x in d['loops']]}, indent=2))"

loop-heartbeat:
	python3 scripts/noos_loop_heartbeat_v1.py --write-receipt --json

backlog:
	@python3 -c "import json; d=json.load(open('data/noos-unified-upgrade-backlog-v1.json')); print(json.dumps({'tiers':d['tier_definitions'],'summary':d['summary'],'next':[x['id'] for x in d['items'] if x.get('tier')=='T1' and x.get('status')=='open']}, indent=2))"

urls:
	bash scripts/check_production_urls.sh
