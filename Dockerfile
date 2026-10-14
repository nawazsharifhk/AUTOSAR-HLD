FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create required data directories
RUN mkdir -p data/documents data/processed data/chroma data/reports data/sample_hld

# Seed sample data
RUN python scripts/generate_sample_hld.py && python scripts/seed_sample_data.py || true

EXPOSE 8000 8501

# Default startup script running both backend and frontend
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
