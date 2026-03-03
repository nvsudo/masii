FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the bot in polling mode with unbuffered output (for real-time logs)
CMD ["python", "-u", "bot.py"]
