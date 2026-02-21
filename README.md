# Learn Robotics

## Installation
When I `pip install lerobot` it installs an older version 0.3.2. To get the latest version tag 0.4.3, I need to build from source. In both the latest version and the one downloaded from PyPI, there is a hard dependency on PyTorch versions < 2.8, not sure why this is. PyTorch 2.8 wheels are only available for python 3.13. I have python 3.14 on my system, so all the hackery I have done below would've been needed even if PyPI gave me the right version.

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

This should install lerobot with the following extras:

| Extra           | GPU                     | CPU                    |
| --------------- | ----------------------- | ---------------------- |
| Simulation Envs | N/A                     | aloha, pusht           |
| Features        | async, peft             | async, peft            |
| Motors          | N/A                     | feetech                |
| Policies        | smolvla, groot(?), xvla | smolvla, xvla, hilserl |
| Robots          | kinematics              | kinematics, phone      |

If I want to install other extras, remember to first uninstall lerobot and then re-install with the new extras.

### Details

The highest python version that pytorch 2.7 supports is 3.13. So first I have to set up my project to use that.

```shell
uv python install 3.13
```

Since this is now `uv`'s "default" python, when I `uv init` any project, it will pin this python version in `.python-version` file. The generated `pyproject.toml` file will have `requires-python = ">=3.13"`. However, because of the greater-than qualifier, when I try to install pytorch with the downloaded wheel, it will complain/outright fail. I need to make the dependency exact. I have changed it to `==3.13.11` which is my exact python 3.13 version.

#### Build lerobot
After cloning the lerobot repo run the following command in the repo root:
```shell
uv build
```
This will create a `./dist` directory with the wheel file in there.

Copy it here.
```
cp path/to/lerobot/dist/lerobot-0.4.3-py3-none-any.whl .
```

#### Download older pytorch
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

#### Install Deps
Before installing the local wheels install some of the depedencies by hand so it is easy to debug installation failures.
  * numpy < 2.4
  * gym-hil - needed by hilserl extra.
  * labmaze - needed by aloha. This is a problematic installation. They have build distributions for python versions 3.6, 3.7, 3.8, and 3.9, but nothing for 3.13. So `uv add labmaze` will try to build the source. But it will fail because the build needs a very old version of bazel, 5.4.1. Current version is 9.x. To get over this I first installed bazelisk `pacman -S bazelisk`, set the .bazelversion file in this repo to the older bazel version, and then installed labmaze.

#### Install Rest
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

## Common Commands

```shell
lerobot-find-port
```

```shell
v4l2-ctl --list-devices | grep -A 3 'BRIO'
v4l2-ctl --list-devices | grep -A 3 'WEBCAM'
lerobot-find-cameras opencv 2>&1 | grep -B 2 -A 10 'Name:.*/dev/video48'
```

```shell
set -x YANTRA_ROBOT '/dev/ttyACM0'
set -x YANTRA_TELEOP '/dev/ttyACM1'
set -x YANTRA_GRIPPER_CAMERA '/dev/video50'
set -x YANTRA_ENV_CAMERA '/dev/video0'
```

```shell
lerobot-calibrate --robot.type=so101_follower --robot.port=$YANTRA_ROBOT --robot.id=yantra_robot
```

```shell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=$YANTRA_TELEOP --teleop.id=yantra_teleop
```

PosixPath('/home/avilay/.cache/huggingface/lerobot/calibration/robots/so_follower')

PosixPath('/home/avilay/.cache/huggingface/lerobot/calibration/robots/so_follower/yantra_1.json')

```shell
lerobot-teleoperate \
--robot.type=so101_follower \
--robot.port=$YANTRA_ROBOT \
--robot.id=yantra_robot \
--robot.cameras="{gripper: {type: opencv, index_or_path: $YANTRA_GRIPPER_CAMERA, width: 640, height: 480, fps: 30}, env: {type: opencv, index_or_path: $YANTRA_ENV_CAMERA, width: 640, height: 480, fps: 30}}" \
--teleop.type=so101_leader \
--teleop.port=$YANTRA_TELEOP \
--teleop.id=yantra_teleop \
--display_data=true
```

```shell
lerobot-record \
--robot.type=so101_follower \
--robot.port=$YANTRA_ROBOT \
--robot.id=yantra_robot \
--robot.cameras="{gripper: {type: opencv, index_or_path: $YANTRA_GRIPPER_CAMERA, width: 640, height: 480, fps: 30}, env: {type: opencv, index_or_path: $YANTRA_ENV_CAMERA, width: 640, height: 480, fps: 30}}" \
--teleop.type=so101_leader \
--teleop.port=$YANTRA_TELEOP \
--teleop.id=yantra_teleop \
--display_data=true \
--dataset.repo_id=avilay/pick-and-place-4 \
--dataset.num_episodes=5 \
--dataset.single_task="Pick and place the juice box" \
--dataset.push_to_hub=False \
--dataset.episode_time_s=20 \
--dataset.reset_time_s=10
```

To make my life easier and not have to find ports everytime I disconnect and reconnect my laptop to my USB hubs, I have written `setenv.py` script that will set the YANTRA_* environment variables by automatically detecting the USB ports on which my robots and cameras are connected. I need to follow this sequence:
  1. `cd <projectdir>`
  2. `source .venv/bin/activate.fish`
  3. `python setenv.py | source`

I have put these three commands in a fish function called `robotics` in my fish config.


In case I forget to upload my dataset when recording -
```shell
huggingface-cli upload avilay/pick_and_place ~/.cache/huggingface/lerobot/avilay/pick_and_place --repo-type dataset
```

```python
from huggingface_hub import HfApi

hub_api = HfApi()
hub_api.create_tag("avilay/pick_and_place", tag="_version_", repo_type="dataset")
```
Here `_version_` is whatever is the `codebase_version` in the info.json in the meta dataset cache.

```shell
mkdir outputs

sudo docker container run \
  --gpus all \
  --mount type=bind,source=./outputs,target=/learn-robotics/outputs \
  -v /dev/shm:/dev/shm \
  -it \
  avilay/learn-robotics:v0.1.0 \
  /bin/bash
```

```shell
source .venv/bin/activate

export HUGGINGFACE_TOKEN=<hftok>
export WANDB_API_KEY=<wandbapi>
export JOB_NAME='pick_and_place_v0.1.0'
export DATASET='avilay/pick_and_place_5'
git config --global credential.helper store
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential
wandb login --verify
rm -fr outputs/train/${JOB_NAME}

lerobot-train \
  --dataset.repo_id=${DATASET} \
  --policy.type=act \
  --output_dir=outputs/train/${JOB_NAME} \
  --job_name=${JOB_NAME} \
  --wandb.enable=true \
  --policy.repo_id=avilay/${JOB_NAME} \
  --steps=1000
```

On an A10 it takes 3 mins / 1000 steps to train. To train a full 100,000 steps it will take 5 hours.

