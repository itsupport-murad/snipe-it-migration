FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy migration script
COPY migrate.py .

# Create backup directory
RUN mkdir -p /app/backup

# Copy backup file
COPY backup/ /app/backup/

# Run migration automatically when container starts
CMD ["python", "migrate.py"]
