FROM python:3.11-slim

WORKDIR /app

# Install system deps for weasyprint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
    libgdk-pixbuf2.0-0 libglib2.0-0 shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:80/health'); assert r.status_code == 200"

# Run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
