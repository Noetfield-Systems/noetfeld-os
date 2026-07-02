.PHONY: test gate demo build-gate-js install inbox cloud-worker autorun-once autorun autorun-status urls

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

urls:
	bash scripts/check_production_urls.sh
