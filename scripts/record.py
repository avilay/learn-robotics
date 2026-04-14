import logging
import os
import readline  # noqa: F401
from pathlib import Path

import click
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import build_dataset_frame, hw_to_dataset_features
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.constants import ACTION, OBS_STR
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

from zeromode.utils import ticks

logging.getLogger("draccus.parsers").setLevel(logging.ERROR)
logging.getLogger("qt.qpa.services").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.ERROR, handlers=(logging.StreamHandler(),), force=True
)


ROBOT = os.environ["ZEROMODE_ROBOT"]
TELEOP = os.environ["ZEROMODE_TELEOP"]
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


def make_teleop() -> SO101Leader:
    teleop_cfg = SO101LeaderConfig(port=TELEOP, id="yantra_teleop")
    return SO101Leader(teleop_cfg)


def make_dataset(robot: SO101Follower, task: str) -> LeRobotDataset:
    action_features = hw_to_dataset_features(robot.action_features, "action")  # type: ignore
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}
    return LeRobotDataset.create(
        repo_id=f"avilay/{task}",
        fps=30,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4,
    )


@click.command()
@click.option(
    "--num-episodes", default=5, help="Number of episodes to record (defaults to 5)."
)
@click.option(
    "--episode-time",
    default=60,
    help="Duration of the episode in seconds (defaults to 60).",
)
@click.option(
    "--reset-time", default=60, help="Reset time in seconds (defaults to 60)."
)
@click.option(
    "--desc",
    default="",
    help="Task description. If not proivded, TASK used.",
)
@click.option("--local", is_flag=True, help="Keep the generated dataset local.")
@click.argument("task")
def main(num_episodes, episode_time, reset_time, desc, local, task):
    desc = desc or task

    robot = make_robot()
    teleop = make_teleop()
    dataset = make_dataset(robot, task)

    robot.connect(calibrate=False)
    teleop.connect(calibrate=False)

    init_rerun(session_name="recording")

    for episode in range(1, num_episodes + 1):
        log_say(f"Recording episode {episode}")
        for _ in ticks(FPS, episode_time):
            obs = robot.get_observation()
            action = teleop.get_action()
            robot.send_action(action)

            obs_frame = build_dataset_frame(dataset.features, obs, prefix=OBS_STR)
            action_frame = build_dataset_frame(dataset.features, action, prefix=ACTION)
            ds_frame = {**obs_frame, **action_frame, "task": task}
            dataset.add_frame(ds_frame)
            log_rerun_data(observation=obs, action=action, compress_images=True)
        dataset.save_episode()

        log_say("Reset the environment.")
        for _ in ticks(FPS, reset_time):
            robot.send_action(teleop.get_action())

    dataset.finalize()
    robot.disconnect()
    teleop.disconnect()
    if not local:
        dataset.push_to_hub()


if __name__ == "__main__":
    main()
