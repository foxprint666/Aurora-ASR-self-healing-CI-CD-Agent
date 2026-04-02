# Optimized Dockerfile for Hugging Face Spaces (Aurora ASR)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/asr \
    PATH=/home/asr/.local/bin:$PATH

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Hugging Face requires UID 1000)
RUN useradd -m -u 1000 asr
RUN chown -R asr:asr /app
USER asr

# Install Python dependencies
COPY --chown=asr:asr requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user gradio google-genai

# Copy project files
COPY --chown=asr:asr . .

# Install the package in editable mode
RUN pip install --user -e .

# Expose the default Hugging Face port
EXPOSE 7860

# Start the Gradio dashboard
CMD ["python", "app.py"]