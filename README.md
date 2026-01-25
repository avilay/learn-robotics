# Learn Robotics

When I `pip install lerobot` it installs an older version 0.3.2. To get the latest version tag 0.4.3, I need to build from source. In both the latest version and the one downloaded from PyPI, there is a hard dependency on PyTorch versions < 2.8, not sure why this is. PyTorch 2.8 wheels are only available for python 3.13. I have python 3.14 on my system, so all the hackery I have done below would've been needed even if PyPI gave me the right version.

## Get Started

These instructions will work for any 64-bit Linux system.

```shell
> git clone git@github.com:huggingface/lerobot.git
> cd lerobot
> uv build
> cd ..
> git clone git@github.com:avilay/learn-robotics.git
> cd learn-robotics
> mkdir wheels
> cd wheels
> wget -c https://download.pytorch.org/whl/cpu/torch-2.8.0%2Bcpu-cp313-cp313-manylinux_2_28_x86_64.whl#sha256=8f81dedb4c6076ec325acc3b47525f9c550e5284a18eae1d9061c543f7b6e7de
> cp ../../lerobot/dist/lerobot-0.4.3-py3-none-any.whl .
> cd ..
> uv sync
> source .venv/bin/activate.fish
```

This should install lerobot with hilserl and aloha extras. If I want to install other extras, remember to first uninstall lerobot and then re-install with the new extras.

## Details

The highest python version that pytorch 2.7 supports is 3.13. So first I have to set up my project to use that.

```shell
uv python install 3.13
```

Since this is now `uv`'s "default" python, when I `uv init` any project, it will pin this python version in `.python-version` file. The generated `pyproject.toml` file will have `requires-python = ">=3.13"`. However, because of the greater-than qualifier, when I try to install pytorch with the downloaded wheel, it will complain/outright fail. I need to make the dependency exact. I have changed it to `==3.13.11` which is my exact python 3.13 version.

### Build lerobot
After cloning the lerobot repo run the following command in the repo root:
```shell
uv build
```
This will create a `./dist` directory with the wheel file in there.

Copy it here.
```
cp path/to/lerobot/dist/lerobot-0.4.3-py3-none-any.whl .
```

### Download older pytorch
On CPU-only systems, head over to https://download.pytorch.org/whl/cpu and get the appropriate 2.7. It is available for python versions 3.10, 3.11, 3.12, and 3.13. Python wheels follow the following naming convention:
```
{distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl
```

I downloaded `torch-2.7.1+cpu-cp313-cp313-manylinux_2_28_x86_64.whl`:
  * version = 2.7.1
  * build = cpu
  * python = cpython 3.13
  * ABI = cpython 3.13
  * platform = manylinux_2_28_x86_64

### Install Deps
Before installing the local wheels install some of the depedencies by hand so it is easy to debug installation failures.
  * numpy < 2.4 - I forgot which of the downstream deps needs this.
  * gym-hil - needed by hilserl extra.
  * labmaze - needed by aloha. This is a problematic installation. They have build distributions for python versions 3.6, 3.7, 3.8, and 3.9, but nothing for 3.13. So `uv add labmaze` will try to build the source. But it will fail because the build needs a very old version of bazel, 5.4.1. Current version is 9.x. To get over this I first installed bazelisk `pacman -S bazelisk`, set the .bazelversion file in this repo to the older bazel version, and then installed labmaze.

### Install Rest
Now I am ready to install pytorch 
```shell
uv add torch-2.7.1+cpu-cp313-cp313-manylinux_2_28_x86_64.whl
```
This will automatically add `tools.uv.sources` section to my pyproject.toml file. 

Install `lerobot[hilserl,aloha]`
```shell
uv add --optional aloha,hilserl lerobot-0.4.3-py3-none-any.whl
```
This will add lerobot to the `tools.uv.sources` section.
