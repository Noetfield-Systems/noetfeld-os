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

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir -e .

EXPOSE 8001

CMD ["sh", "-c", "uvicorn run:app --host 0.0.0.0 --port ${PORT:-8001}"]
