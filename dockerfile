FROM python:3.10-slim-bookworm

# Install curl (needed to fetch uv installer)
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# # Install uv (fast dependency manager)
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app


COPY requirements.txt main.py frontend.py .env /pdfs /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Environment variables
ENV CHROMA_DIR=./chroma_db \
    AUDIO_DIR=./static/audio \
    STATIC_URL=/static \
    HOST=0.0.0.0 \
    PORT=8000

# Expose backend (Uvicorn) and frontend (Streamlit) ports
EXPOSE 8000
EXPOSE 8501

# Run both uvicorn + streamlit in same container
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0"]
