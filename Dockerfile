# Start from an official Python image

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies that geospatial packages need
RUN apt-get update && apt-get install -y \
	gdal-bin \
	libgdal-dev \
	libpq-dev \
	gcc \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements first before copying code
COPY requirements.txt

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the code
COPY . .

# Default command runs the ingestion script
CMD ["python", "ingestion/firms_ingest.py"]