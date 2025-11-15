# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (including Stockfish!)
RUN apt-get update && apt-get install -y \
    stockfish \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set default command
CMD ["python3"]