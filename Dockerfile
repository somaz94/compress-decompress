# Use an official lightweight Python image.
# Python is used here for the entry script; you could use any other lightweight base image.
FROM python:3.13-slim

# Install compression and decompression tools
# Specify versions as available. Note: Debian-based versions may not match Alpine directly and need to be verified.
RUN apt-get update && \
    apt-get install -y \
    zip=3.0-13 \
    unzip=6.0-28 \
    tar=1.34+dfsg-1.2+deb12u1 \
    gzip=1.12-1 \
    bzip2=1.0.8-5+b1 \
    xz-utils=5.4.1-0.2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a user and group
RUN addgroup --system app && adduser --system --group app

# Set the working directory and permissions
WORKDIR /usr/src
RUN chown app:app /usr/src

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY --chown=app:app entrypoint.py .

# Switch to non-root user
USER app

# File to execute when the docker container starts up (`entrypoint.py`)
ENTRYPOINT ["python", "/usr/src/entrypoint.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -fs http://localhost:80/ || exit 1