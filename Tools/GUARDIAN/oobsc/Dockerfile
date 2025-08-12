FROM python:3.11-slim
WORKDIR /app

# Copy app
COPY app.py /app/app.py

# OS deps (for healthcheck) + Python deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends wget \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir fastapi uvicorn pydantic

EXPOSE 8000

# Optional: container-level healthcheck so compose can gate AI
HEALTHCHECK --interval=2s --timeout=1s --retries=20 CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
