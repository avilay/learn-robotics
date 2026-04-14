import os
import time
from pathlib import Path

import click
import torch as th
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.utils import build_dataset_frame, hw_to_dataset_features
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.utils import make_robot_action, prepare_observation_for_inference
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
from lerobot.utils.utils import log_say

from zeromode.utils import reset_robot_pos, ticks

ROBOT = os.environ["ZEROMODE_ROBOT"]
GRIPPER_CAMERA = Path(os.environ["ZEROMODE_GRIPPER_CAMERA"])
ENV_CAMERA = Path(os.environ["ZEROMODE_ENV_CAMERA"])
FPS = 30


def make_robot() -> SO101Follower:
    robot_cfg = SO101FollowerConfig(
        port=ROBOT,
        id="yantra_robot",
        cameras={
            "gripper": OpenCVCameraConfig(
                index_or_path=GRIPPER_CAMERA, width=640, height=480, fps=30, warmup_s=3
            ),
            "env": OpenCVCameraConfig(
                index_or_path=ENV_CAMERA, width=640, height=480, fps=30, warmup_s=3
            ),
        },
    )
    return SO101Follower(robot_cfg)


@click.command()
@click.option(
    "--num-episodes", default=5, help="Number of episodes to eval (defaults to 5)."
)
@click.option(
    "--episode-time",
    default=60,
    help="Duration of the episode in seconds (defaults to 60).",
)
@click.option(
    "--reset-time", default=60, help="Reset time in seconds (defaults to 60)."
)
@click.argument("task")
def main(num_episodes, episode_time, reset_time, local, task):
    robot = make_robot()

    action_features = hw_to_dataset_features(robot.action_features, "action")  # type: ignore
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

    policy = ACTPolicy.from_pretrained("avilay/pick_and_place_v1.0.0")

    policy_preproc, policy_postproc = make_pre_post_processors(
        policy_cfg=policy,  # type: ignore
        pretrained_path="avilay/pick_and_place_v1.0.0",
        preprocessor_overrides={"device_processor": {"device": "cpu"}},
        postprocessor_overrides={"device_processor": {"device": "cpu"}},
    )

    robot.connect(calibrate=False)

    policy.reset()
    policy_preproc.reset()
    policy_postproc.reset()
    cpu = th.device("cpu")

    for episode in range(1, num_episodes + 1):
        log_say(f"Running episode {episode}")
        for _ in ticks(FPS, episode_time):
            obs = robot.get_observation()
            obs_frame = build_dataset_frame(dataset_features, obs, prefix="OBS_STR")

            with th.inference_mode():
                obs_input = prepare_observation_for_inference(
                    obs_frame, cpu, robot_type=robot.robot_type
                )
                obs_input_processed = policy_preproc(obs_input)
                action_output = policy.select_action(obs_input_processed)
                action_output_processed = policy_postproc(action_output)

            action = make_robot_action(action_output_processed, dataset_features)
            robot.send_action(action)

        log_say("Reset environment")
        start = time.perf_counter()
        reset_robot_pos(robot)
        elapsed_time = time.perf_counter() - start
        remaining_time = reset_time - elapsed_time
        if remaining_time > 0:
            time.sleep(remaining_time)

    robot.disconnect()
