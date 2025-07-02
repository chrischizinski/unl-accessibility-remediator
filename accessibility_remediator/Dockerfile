FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/
COPY web/ ./web/
COPY templates/ ./templates/

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/reports

# Make the main script executable
COPY main.py .
RUN chmod +x main.py

# Expose port for web interface
EXPOSE 8000

# Default command runs the CLI help
CMD ["python", "main.py", "--help"]