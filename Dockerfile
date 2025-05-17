FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN pip install -e .


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
