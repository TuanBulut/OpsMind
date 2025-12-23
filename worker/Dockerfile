FROM python:3.9-slim

WORKDIR /app

# Install required Python packages
RUN pip install --no-cache-dir mysql-connector-python requests

# Copy worker script
COPY ai_worker.py .

# Run the worker
CMD ["python", "ai_worker.py"]