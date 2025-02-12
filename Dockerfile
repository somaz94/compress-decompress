# Use an official lightweight Python image.
# Python is used here for the entry script; you could use any other lightweight base image.
FROM python:3.13-slim

# Install compression and decompression tools
# Specify versions as available. Note: Debian-based versions may not match Alpine directly and need to be verified.
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

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY app/* .

# File to execute when the docker container starts up (main.py)
ENTRYPOINT ["python", "/usr/src/main.py"]
