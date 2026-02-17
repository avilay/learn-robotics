FROM nvidia/cuda:13.1.1-cudnn-runtime-ubuntu24.04
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends curl wget ca-certificates git
git config --global advice.detachedHead false
git clone https://github.com/avilay/learn-robotics.git
cd lerobot
git checkout tags/v0.4.3
uv build
cd ..
https://github.com/avilay/learn-robotics.git
cd learn-robotics
mkdir wheels
cd wheels
wget https://download.pytorch.org/whl/cu128/torch-2.7.0%2Bcu128-cp313-cp313-manylinux_2_28_x86_64.whl#sha256=d2f69f909da5dc52113ec66a851d62079f3d52c83184cf64beebdf12ca2f705c
mv torch-2.7.0+cu128-cp313-cp313-manylinux_2_28_x86_64.whl torch-2.7.whl
wget https://download.pytorch.org/whl/cpu/torchvision-0.22.1%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl#sha256=a93c21f18c33a819616b3dda7655aa4de40b219682c654175b6bbeb65ecc2e5f
cp ../../lerobot/dist/lerobot-0.4.3-py3-none-any.whl .
