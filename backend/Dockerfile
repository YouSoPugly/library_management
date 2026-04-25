# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Load env file (optional but useful)
ENV PYTHONUNBUFFERED=1

# Expose port (default fallback)
EXPOSE 8000

# Run app (uses PORT from .env)
CMD ["python", "main.py"]
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt