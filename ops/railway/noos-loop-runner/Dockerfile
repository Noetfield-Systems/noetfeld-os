FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends make \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt pyproject.toml Makefile ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY docs/_NOOS_AGENT/UPGRADE_MANIFEST.json ./docs/_NOOS_AGENT/UPGRADE_MANIFEST.json
COPY ops/railway/noos-loop-runner/BUILD_SHA ./BUILD_SHA
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

# Land entrypoint in BOTH paths. Railway service startCommand history drifts
# between /app/server.py and ops/railway/noos-loop-runner/server.py; missing
# /app/server.py caused healthcheck FAILED (container: No such file).
COPY ops/railway/noos-loop-runner/server.py ./ops/railway/noos-loop-runner/server.py
COPY ops/railway/noos-loop-runner/server.py ./server.py
RUN test -f /app/server.py \
  && test -f /app/ops/railway/noos-loop-runner/server.py

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/server.py"]
