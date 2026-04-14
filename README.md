# Learn Robotics

See [notes.md](notes.md) for learning notes and concepts.

## Installation

Standard steps - clone the repo and sync uv.

```shell
> git clone git@github.com:avilay/learn-robotics
> cd learn-robotics
> uv sync --extra cpu
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

#### Problematic Packages

* `mujuco`: Needs python 3.13. It does not have pre-built wheels beyond that, so if python version is higher then it will try to build mujoco from source and will run into errors. Easiest to just pin the python version to 3.13.
* `labmaze`: labmaze - needed by aloha. They have build distributions for python versions 3.6, 3.7, 3.8, and 3.9, but nothing for 3.13. Going down to python 3.9 was a bit much. `uv add labmaze` will try to build the source, but it will fail because the build needs a very old version of bazel, 5.4.1. Current version is 9.x. To get over this I first installed bazelisk `pacman -S bazelisk`, set the .bazelversion file in this repo to the older bazel version, and then installed labmaze.

## Initial Setup

Find the ports on which the robots are connected:

```shell
lerobot-find-port
```

Find the ports on which the cameras are connected:

```shell
v4l2-ctl --list-devices | grep -A 3 'BRIO'
v4l2-ctl --list-devices | grep -A 3 'WEBCAM'
lerobot-find-cameras opencv 2>&1 | grep -B 2 -A 10 'Name:.*/dev/video48'
```

Calibrate the robots:

```shell
lerobot-calibrate --robot.type=so101_follower --robot.port=<port> --robot.id=yantra_robot

lerobot-calibrate --teleop.type=so101_leader --teleop.port=<port> --teleop.id=yantra_teleop
```

The calibration files are stored here:

```
~/.cache/huggingface/lerobot/calibration/robots/so_follower/yantra_robot.json
~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/yantra_teleop.json
```

## Environment Setup

The ports are needed for all the APIs and CLIs. To make my life easier and not have to find which USB ports the robots and cameras are connected to everytime I disconnect and reconnect my laptop to my USB hubs, I have written `setenv.py` script that will set the `ZEROMODE_*` environment variables by automatically detecting the relevant USB ports. I need to follow this sequence:

```shell
cd ~/projects/github/learn-robotics
source .venv/bin/activate.fish
python scripts/setenv.py | source
```

I have put these three commands in a fish function called `robotics` in my fish config. So in steady-state I just run this command anywhere in my terminal -

```fish
robotics
```

I can then run the `./scripts/wirecheck.py` stand-alone script to ensure all the wires are connected to all the right devices.

```shell
python scripts/wirecheck.py
```

## Common Tasks

### Teleoperating the Robot

```shell
lerobot-teleoperate \
--robot.type=so101_follower \
--robot.port=$ZEROMODE_ROBOT \
--robot.id=yantra_robot \
--robot.cameras="{gripper: {type: opencv, index_or_path: $ZEROMODE_GRIPPER_CAMERA, width: 640, height: 480, fps: 30, warmup_s: 3}, env: {type: opencv, index_or_path: $ZEROMODE_ENV_CAMERA, width: 640, height: 480, fps: 30, warmup_s: 3}}" \
--teleop.type=so101_leader \
--teleop.port=$ZEROMODE_TELEOP \
--teleop.id=yantra_teleop \
--display_data=true
```

### Recording Training Data

```shell
lerobot-record \
--robot.type=so101_follower \
--robot.port=$ZEROMODE_ROBOT \
--robot.id=yantra_robot \
--robot.cameras="{gripper: {type: opencv, index_or_path: $ZEROMODE_GRIPPER_CAMERA, width: 640, height: 480, fps: 30}, env: {type: opencv, index_or_path: $ZEROMODE_ENV_CAMERA, width: 640, height: 480, fps: 30}}" \
--teleop.type=so101_leader \
--teleop.port=$ZEROMODE_TELEOP \
--teleop.id=yantra_teleop \
--display_data=true \
--dataset.repo_id=avilay/pick-and-place-4 \
--dataset.num_episodes=5 \
--dataset.single_task="Pick and place the juice box" \
--dataset.push_to_hub=False \
--dataset.episode_time_s=20 \
--dataset.reset_time_s=10
```

There is no special marker that indicates the end of an episode. The time that I specify as the `--dataset.episode_time` is the marker. The foundation model seems to be resilient to episodes that are longer than the actual task. I have written my own recording script so I don't have to specify all the different params.

```shell
python scripts/record.py
```

#### Uploading Datasets

My record script will automatically upload the dataset to HF's github which will automatically tag it. This is needed during training. In case I need to upload the dataset after the fact, I need to follow this two step process, first to upload it and second to tag it.

```shell
huggingface-cli upload avilay/pick_and_place ~/.cache/huggingface/lerobot/avilay/pick_and_place --repo-type dataset
```

```python
from huggingface_hub import HfApi

hub_api = HfApi()
hub_api.create_tag("avilay/pick_and_place", tag="_version_", repo_type="dataset")
```

Here `_version_` is whatever is the `codebase_version` in the info.json in the meta dataset cache.

## Training

Once on a CUDA-enabled VM download and run the Docker image:

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

Then inside the Docker container run the training script:

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

