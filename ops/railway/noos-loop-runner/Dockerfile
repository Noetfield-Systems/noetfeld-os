FROM python:3.12-slim

WORKDIR /app
ARG NOOS_CACHEBUST=role-circle-v2-20260719
COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
COPY .agent-policy ./.agent-policy
COPY ops/railway/noos-loop-runner/BUILD_SHA ./BUILD_SHA
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

# Land the entrypoint in BOTH locations — Railway startCommand history differs.
RUN mkdir -p /app/ops/railway/noos-loop-runner
COPY ops/railway/noos-loop-runner/server.py /app/ops/railway/noos-loop-runner/server.py
COPY ops/railway/noos-loop-runner/server.py /app/server.py
RUN test -f /app/server.py \
  && test -f /app/ops/railway/noos-loop-runner/server.py \
  && test -d /app/scripts \
  && test -d /app/data \
  && echo "NOOS_CACHEBUST=${NOOS_CACHEBUST}" > /app/ENTRYPOINT_OK

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/server.py"]
