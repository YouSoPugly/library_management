# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Unbuffered logs (important for Docker log streaming)
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# app.main:app = app/ package -> main.py -> app = FastAPI instance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]