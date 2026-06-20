FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY assets/ ./assets/

# Télécharge le modèle YOLO au build (évite le téléchargement au 1er appel)
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

ENV PYTHONPATH=/app
ENV PORT=8001

EXPOSE 8001

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
