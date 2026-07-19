FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY .agent-policy ./.agent-policy
COPY ops/railway/noos-loop-runner/BUILD_SHA ./BUILD_SHA
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

# Explicit mkdir — Railway Metal builder sometimes drops nested COPY parents.
RUN mkdir -p /app/ops/railway/noos-loop-runner
COPY ops/railway/noos-loop-runner/server.py /app/ops/railway/noos-loop-runner/server.py
RUN test -f /app/ops/railway/noos-loop-runner/server.py

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/ops/railway/noos-loop-runner/server.py"]
