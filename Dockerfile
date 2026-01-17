FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (kept minimal)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY uploads ./uploads

# Render/Railway typically provides PORT
ENV PORT=8000

# Seed DB on startup (demo-friendly) and start API
CMD python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
