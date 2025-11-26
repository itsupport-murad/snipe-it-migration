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

# Keep container running so we can exec into it
ENTRYPOINT []
CMD ["/bin/sh", "-c", "echo 'Migration helper ready. Run: python migrate.py' && tail -f /dev/null"]
