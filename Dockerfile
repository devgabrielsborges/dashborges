# Use official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install build tools and poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy dependency definitions
COPY pyproject.toml README.md ./

# Install dependencies (excluding dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application source code
COPY . .

# Create directories for persistent storage
RUN mkdir -p /app/data /app/config /app/logs && \
    chmod -R 777 /app/data /app/config /app/logs

# Create a non-root user for security
RUN useradd -m -u 1000 dashborges && \
    chown -R dashborges:dashborges /app

# Switch to non-root user
USER dashborges

# Define volumes for persistent data storage
VOLUME ["/app/data", "/app/config", "/app/logs"]

# Expose ports for API and Streamlit dashboard
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/transactions/ || exit 1

# Default command to run the application
ENTRYPOINT ["python", "run_app.py"]
