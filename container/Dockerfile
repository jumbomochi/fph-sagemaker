# container/Dockerfile

# Use a stable, official Python image as the base
FROM python:3.9-slim

# Install necessary system packages (if any, none needed for this simple case)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ...
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /opt/program

# Install Python dependencies (pandas, scikit-learn)
# IMPORTANT: This assumes you have a container/requirements.txt file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the training script and the serving entry point
# We'll use the 'src/model_sklearn.py' as our training script inside the container
COPY src/model_sklearn.py train
COPY container/serve /opt/program/serve

# Define entry point for SageMaker:
# SageMaker expects a 'train' script at /opt/program/train and 'serve' at /opt/program/serve
ENV SAGEMAKER_PROGRAM model_sklearn.py