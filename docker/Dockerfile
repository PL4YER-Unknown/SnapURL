FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY .. /app/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start app using Gunicorn
CMD ["gunicorn", "app:create_app()", "-c", "docker/gunicorn.conf.py"]
