# Simple example Dockerfile for SageMaker BYOC
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY serve /app/serve
CMD ["python", "serve/serve.py"]
