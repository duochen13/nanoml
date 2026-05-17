FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.0 \
    uvicorn==0.24.0 \
    torch==2.1.0 \
    numpy==1.24.0

# Copy server code
COPY server.py /app/
COPY client.py /app/

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
