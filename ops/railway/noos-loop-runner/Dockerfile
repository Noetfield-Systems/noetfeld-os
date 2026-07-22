FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY docs/_NOOS_AGENT/UPGRADE_MANIFEST.json ./docs/_NOOS_AGENT/UPGRADE_MANIFEST.json
COPY ops/railway/noos-loop-runner/BUILD_SHA ./BUILD_SHA
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

COPY ops/railway/noos-loop-runner/server.py ./ops/railway/noos-loop-runner/server.py
# Compatibility: some Railway service settings still invoke /app/server.py.
COPY ops/railway/noos-loop-runner/server.py ./server.py

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "ops/railway/noos-loop-runner/server.py"]
