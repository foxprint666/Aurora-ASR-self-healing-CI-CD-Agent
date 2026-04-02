# Multi-stage build for OpenEnv ASR

# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

LABEL maintainer="OpenEnv Contributors"
LABEL description="OpenEnv Automated Software Repair Environment"
LABEL version="0.2.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Install Python packages
RUN pip install --no-cache /wheels/*

# Copy project
COPY . .

# Install package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 asr
USER asr

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; import environment; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "training.train_hybrid_agent", "--episodes", "100", "--device", "cuda"]