FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py core.py floor_projection.py commercial_team.py portfolio_studio.py company_workforce_binding_v1.json ./
COPY static ./static
RUN mkdir -p /data && python -m py_compile app.py core.py floor_projection.py commercial_team.py portfolio_studio.py
EXPOSE 8080
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080"]
