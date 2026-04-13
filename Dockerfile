FROM python:3.12-slim

# install system deps (needed by some pandas/numpy builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install Python deps first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY data/ ./data/
COPY src/  ./src/

# pre-generate the dataset if CSVs are absent (useful for fresh image builds)
RUN python data/generate_banking_ops.py

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "src/app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true"]
