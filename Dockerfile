# 🏗 Stage 1: Build dependencies
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /usr/src

# Copy only necessary files (avoid copying unnecessary files like .git, backup, tests, etc.)
COPY app/ app/

# 🏗 Final Stage: Minimal runtime image
FROM python:3.13-slim

# Install only necessary system utilities (avoid unnecessary dependencies)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    zip unzip tar gzip bzip2 xz-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src

# Copy only necessary files from builder
COPY --from=builder /usr/src/app /usr/src/app

# Run the main script
ENTRYPOINT ["python", "/usr/src/app/main.py"]