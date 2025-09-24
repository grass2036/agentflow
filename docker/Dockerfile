# AgentFlow Docker Image
FROM python:3.11-slim

LABEL maintainer="AgentFlow Team <contact@agentflow.dev>"
LABEL description="AgentFlow - AI Agent Orchestration Framework"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install AgentFlow in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/plugins

# Set environment variables
ENV PYTHONPATH=/app
ENV AGENTFLOW_LOG_LEVEL=INFO
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port for web services
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import agentflow; print(agentflow.get_version())" || exit 1

# Default command
CMD ["agentflow", "status"]