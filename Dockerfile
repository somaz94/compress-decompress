# Use an official lightweight Python image.
FROM python:3.13-slim

# Install compression and decompression tools
RUN apt-get update && \
    apt-get install -y \
    zip \
    unzip \
    tar \
    gzip \
    bzip2 \
    xz-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container    
WORKDIR /usr/src

# Copy all files from app directory
COPY app/ .

# File to execute when the docker container starts up
ENTRYPOINT ["python", "/usr/src/main.py"]