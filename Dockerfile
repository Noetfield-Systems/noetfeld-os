FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends make \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml Makefile ./
COPY noetfield_gate ./noetfield_gate
COPY audit ./audit
COPY export ./export
COPY portal ./portal
COPY public_site ./public_site
COPY *.py ./
COPY base_policy.json corridor_policy.json ./

# Dedicated NOOS loop runtime payload. The Railway service is configured to
# build from this repository root; the entrypoint copied by *.py is legacy.
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY docs/_NOOS_AGENT/UPGRADE_MANIFEST.json ./docs/_NOOS_AGENT/UPGRADE_MANIFEST.json
COPY ops/railway/noos-loop-runner/BUILD_SHA ./BUILD_SHA
COPY ops/railway/noos-loop-runner/server.py ./server.py

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir -e . \
  && python -m py_compile /app/server.py /app/scripts/noos_loop_runner_v1.py \
  && test -f /app/data/noos-24-7-loops-v1.json

EXPOSE 8080
CMD ["python3", "/app/server.py"]
