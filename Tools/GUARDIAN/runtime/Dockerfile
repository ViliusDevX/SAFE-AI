FROM python:3.11-slim
WORKDIR /app
COPY guarded_ai.py /app/guarded_ai.py
RUN pip install requests
ENV OOBSC_URL=http://oobsc:8000
CMD ["python", "guarded_ai.py"]
