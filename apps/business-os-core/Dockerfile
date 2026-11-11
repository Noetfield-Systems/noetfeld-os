FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py core.py brain_pulse.py product_loops.py founder_portfolio_bridge.py venture_company_os.py venture_decision_bridge.py founder_signal_transport.py sina_work_bridge.py paperclip_bridge.py product_portfolio_seed_v1.json company_workforce_binding_v1.json ./
COPY static ./static
RUN mkdir -p /data && python -m py_compile app.py core.py venture_company_os.py brain_pulse.py venture_decision_bridge.py paperclip_bridge.py product_loops.py founder_portfolio_bridge.py founder_signal_transport.py sina_work_bridge.py
RUN python -c "import core, app, venture_company_os, venture_decision_bridge, sina_work_bridge, founder_signal_transport, founder_portfolio_bridge"
EXPOSE 8080
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080"]
