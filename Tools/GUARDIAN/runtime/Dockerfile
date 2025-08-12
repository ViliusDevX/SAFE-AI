FROM python:3.11-slim
WORKDIR /app

COPY guarded_ai.py /app/guarded_ai.py
COPY misbehave.py  /app/misbehave.py
COPY decoys/       /app/decoys/

RUN pip install --no-cache-dir requests

CMD ["python", "/app/guarded_ai.py"]
