# ─── Build: Python 3.11 slim ────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Runtime env defaults (override via docker run -e or .env)
ENV PORT=5000 \
    FLASK_DEBUG=false \
    WATSONX_URL=https://us-south.ml.cloud.ibm.com \
    WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

EXPOSE 5000

CMD ["python", "app.py"]
