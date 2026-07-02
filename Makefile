.PHONY: test gate demo build-gate-js install

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

urls:
	bash scripts/check_production_urls.sh
