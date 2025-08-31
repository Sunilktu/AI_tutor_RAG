FROM python:3.10-slim-bookworm

# Install curl (needed to fetch uv installer)
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# # Install uv (fast dependency manager)
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
# COPY pyproject.toml uv.lock .env ./
COPY requirements.txt main.py frontend.py .env /pdfs /app/

# Install dependencies system-wide (no virtualenv)
# RUN uv pip install --system --no-cache -r <(uv pip compile uv.lock)
# Generate requirements from lock + install globally
# RUN uv pip compile uv.lock -o requirements.txt
# RUN uv pip install --system --no-cache -r requirements.txt
# Install dependencies directly from lock file (system-wide, no venv)
# RUN uv sync --frozen --no-dev --system
# Copy application files
# RUN uv sync
# COPY main.py frontend.py /app/
RUN pip install --no-cache-dir -r requirements.txt
# Environment variables
ENV CHROMA_DIR=./chroma_db \
    # GOOGLE_API_KEY="AIzaSyD0L3CacF3HuaYZHplUwZlKXzNsn4f75JA" \
    AUDIO_DIR=./static/audio \
    STATIC_URL=/static \
    HOST=0.0.0.0 \
    PORT=8000

# Expose backend (Uvicorn) and frontend (Streamlit) ports
EXPOSE 8000
EXPOSE 8501

# Run both uvicorn + streamlit in same container
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0"]
