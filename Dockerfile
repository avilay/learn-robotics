FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends curl wget ca-certificates git
RUN curl -L https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 -o /usr/local/bin/bazel
RUN chmod +x /usr/local/bin/bazel
RUN git clone https://github.com/avilay/learn-robotics.git
RUN cd learn-robotics
