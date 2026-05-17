FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.0 \
    uvicorn==0.24.0 \
    sqlalchemy==2.0.0

# Copy application code
COPY tracker.py /app/
COPY api.py /app/
COPY schema.sql /app/

# Initialize SQLite database
RUN mkdir -p /data && \
    apt-get update && \
    apt-get install -y sqlite3 && \
    sqlite3 /data/lineage.db < schema.sql || true && \
    apt-get remove -y sqlite3 && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 9000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9000"]
