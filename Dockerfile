FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first (to cache layer)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
