FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
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
