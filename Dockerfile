# Jung AI Backend - Root Dockerfile for Railway (build context = repo root)

FROM python:3.11

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKERS=1 \
    WEB_CONCURRENCY=1

WORKDIR /app

# Copy and install backend requirements
COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

# Copy backend source
COPY backend/ /app/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://localhost:{os.environ.get('PORT', 8000)}/health')" || exit 1

CMD ["python", "-c", "import os, uvicorn; port=int(os.environ.get('PORT', 8000)); print(f'Starting on port {port}'); uvicorn.run('api.main:app', host='0.0.0.0', port=port, workers=1, log_level='info')"]


