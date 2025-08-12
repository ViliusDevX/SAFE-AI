FROM python:3.11-slim
WORKDIR /app
COPY honeytoken_detector.py /app/honeytoken_detector.py
COPY egress_gateway.py /app/egress_gateway.py
RUN pip install fastapi uvicorn pydantic httpx
EXPOSE 9000 9100
CMD ["sleep", "infinity"]  # overridden by compose command
