FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY noetfield_gate ./noetfield_gate
COPY scripts ./scripts
COPY data ./data
COPY fixtures ./fixtures
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

COPY ops/fly/noos-loop-executor/server.py ./ops/fly/noos-loop-executor/server.py

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "ops/fly/noos-loop-executor/server.py"]
