# Dockerfile for JODI Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add aiohttp for webhook server
RUN pip install --no-cache-dir aiohttp

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run webhook bot
CMD ["python", "webhook_bot.py"]
