FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Ensure critical packages are installed before continuing
RUN pip install --no-cache-dir uvicorn secure fastapi && \
    pip install --no-cache-dir -r requirements.txt || true

# Copy rest of the code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
