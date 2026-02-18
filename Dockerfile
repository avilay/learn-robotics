FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git python3-dev build-essential micro ffmpeg
RUN curl -LsSf https://hf.co/cli/install.sh | bash
RUN git clone https://github.com/avilay/learn-robotics.git
WORKDIR /learn-robotics
RUN uv sync --extra cuda
