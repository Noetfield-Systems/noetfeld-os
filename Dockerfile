FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY audit ./audit
COPY export ./export
COPY portal ./portal
COPY public_site ./public_site
COPY *.py ./
COPY base_policy.json corridor_policy.json ./
# NOOS loop-runner (Metal builder currently resolves this root Dockerfile for
# noos-loop-runner even when dockerfilePath points at ops/...). Keep entrypoint
# available without breaking gel-api/uvicorn startCommand.
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY .agent-policy ./.agent-policy
RUN mkdir -p /app/ops/railway/noos-loop-runner
COPY ops/railway/noos-loop-runner/server.py /app/server.py
COPY ops/railway/noos-loop-runner/server.py /app/ops/railway/noos-loop-runner/server.py
COPY ops/railway/noos-loop-runner/BUILD_SHA /app/BUILD_SHA

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir -e .

EXPOSE 8001

CMD ["sh", "-c", "uvicorn run:app --host 0.0.0.0 --port ${PORT:-8001}"]
