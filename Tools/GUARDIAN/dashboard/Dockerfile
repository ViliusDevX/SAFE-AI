FROM python:3.11-slim
WORKDIR /app
COPY app.py /app/app.py
COPY templates /app/templates
RUN pip install fastapi uvicorn jinja2 httpx docker
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
