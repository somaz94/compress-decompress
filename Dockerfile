# Single stage on purpose: the app is pure stdlib, so there is no dependency
# install or compile step for a builder stage to isolate — it would only copy
# app/ twice.
FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/somaz94/compress-decompress"
LABEL org.opencontainers.image.description="Compress and decompress files in CI/CD"
LABEL org.opencontainers.image.licenses="MIT"

# Install only necessary system utilities (avoid unnecessary dependencies).
# Kept above the source COPY so editing app/ does not re-run apt.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    zip unzip tar gzip bzip2 xz-utils zstd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Unbuffered: Actions reads stdout through a pipe, where Python would otherwise
# block-buffer and lose the tail of the log if the container dies mid-run.
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src
COPY app/ app/

# No USER instruction on purpose. A container action gets GITHUB_WORKSPACE
# bind-mounted at /github/workspace owned by the runner UID; a non-root user
# cannot write there, which breaks every compress into the workspace.
ENTRYPOINT ["python", "/usr/src/app/main.py"]
