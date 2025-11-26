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

# Create a simple startup script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'echo "Migration helper ready. Run: python migrate.py"' >> /start.sh && \
    echo 'sleep infinity' >> /start.sh && \
    chmod +x /start.sh

# Keep container running
CMD ["/start.sh"]
