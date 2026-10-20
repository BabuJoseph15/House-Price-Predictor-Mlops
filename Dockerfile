FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Verify artifacts exist during build
RUN ls -lh artifacts/

EXPOSE 8000

CMD ["python", "app.py"]
