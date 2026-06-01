FROM python:3.11-slim
WORKDIR /e2e
COPY requirements.txt smoke.py ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "smoke.py"]
