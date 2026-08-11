# Use Python 3.10 Slim to reduce image size and fix build hangs
FROM python:3.10-slim

WORKDIR /app

# Configure libc to prefer IPv4 (Apply FIRST to fix apt-get hangs)
RUN echo "precedence ::ffff:0:0/96 100" >> /etc/gai.conf

# Install system dependencies (Minimal)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    ca-certificates \
    dnsutils \
    iputils-ping \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a user to avoid running as root (required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Copy the unified requirements file (pulls in requirements/audio.txt and
# requirements/auth.txt) into the container
COPY --chown=user requirements.txt requirements.txt
COPY --chown=user requirements/ requirements/

# Install CUDA-enabled PyTorch matching the common NVIDIA CUDA 12.1 runtime
RUN pip install --no-cache-dir torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install madmom separately with --no-build-isolation to use the installed Cython and numpy
RUN pip install --no-cache-dir "numpy<2.0.0" cython
RUN pip install --no-cache-dir --no-build-isolation "madmom>=0.16.1"

# Copy the rest of the backend code
COPY --chown=user . .

# Hugging Face uses port 7860; override PORT for other hosts.
ENV PORT=7860
# Disable Python output buffering so logs show up immediately in HF Spaces
ENV PYTHONUNBUFFERED=1
# Preload models at build time (optional - can be done at runtime too)
# This caches the models in the container image
RUN python scripts/preload_models.py || true

# Single worker: the audio runtime keeps in-process state (loaded models,
# a session registry, a cleanup thread) that isn't safe to share across
# multiple worker processes yet.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
