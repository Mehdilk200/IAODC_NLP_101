FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for FAISS/Torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure data directories exist
RUN mkdir -p data/faiss_index

EXPOSE 8000

# Run API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
