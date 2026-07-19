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

# Flat entrypoint — nested ops/... path was missing at Railway runtime.
COPY ops/railway/noos-loop-runner/server.py ./server.py
RUN test -f /app/server.py && test -d /app/scripts && test -d /app/data

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/server.py"]
