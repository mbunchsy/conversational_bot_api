# Use a specific Python 3.11 base image
FROM python:3.11-slim

# Set environment variables for Python and Django
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create and set working directory
WORKDIR /app

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock* ./

# Install all project dependencies
RUN poetry install --no-root --no-interaction

# Copy the rest of the code
COPY . .

# Make the entry script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port
EXPOSE 8000

# Set the entry script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command for development
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]