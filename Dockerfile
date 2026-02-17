# Stage 1: Builder
# FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04 AS builder
FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git python3-dev build-essential micro \
    && rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 -o /usr/local/bin/bazel \
    && chmod +x /usr/local/bin/bazel
RUN git clone https://github.com/avilay/learn-robotics.git
WORKDIR /learn-robotics
RUN uv sync --extra cuda

# Stage 2: Final image
# FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# COPY --from=builder /learn-robotics /learn-robotics
# WORKDIR /learn-robotics
