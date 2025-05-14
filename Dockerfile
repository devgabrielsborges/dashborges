# Use official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

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

# Create a data directory for persistent storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Define a volume for persistent data storage
VOLUME /app/data

# Expose ports for API and Streamlit dashboard
EXPOSE 8000 8501

# Default command to run the application
ENTRYPOINT ["python", "run_app.py"]
