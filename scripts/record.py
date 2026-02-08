import logging
import os
import readline  # noqa: F401
from pathlib import Path

import click
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.processor import make_default_processors
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
from lerobot.scripts.lerobot_record import record_loop
from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun

logging.getLogger("draccus.parsers").setLevel(logging.ERROR)
logging.getLogger("qt.qpa.services").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.ERROR, handlers=(logging.StreamHandler(),), force=True
)


YANTRA_ROBOT = os.environ["YANTRA_ROBOT"]
YANTRA_TELEOP = os.environ["YANTRA_TELEOP"]
GRIPPER_CAMERA = Path(os.environ["YANTRA_GRIPPER_CAMERA"])
ENV_CAMERA = Path(os.environ["YANTRA_ENV_CAMERA"])


@click.command()
@click.option("--num-episodes", default=5, help="Number of episodes to record.")
@click.option("--episode-time", default=60, help="Duration of the episode in seconds.")
@click.option("--reset-time", default=60, help="Reset time in seconds.")
@click.option(
    "--desc",
    default="",
    help="Task description. If not proivded, the task name is used.",
)
@click.argument("task")
def main(num_episodes, episode_time, reset_time, desc, task):
    desc = desc or task

    robot_cfg = SO101FollowerConfig(
        port=YANTRA_ROBOT,
        id="yantra_robot",
        cameras={
            "gripper": OpenCVCameraConfig(
                index_or_path=GRIPPER_CAMERA, width=640, height=480, fps=30
            ),
            "env": OpenCVCameraConfig(
                index_or_path=ENV_CAMERA, width=640, height=480, fps=30
            ),
        },
    )
    robot = SO101Follower(robot_cfg)

    # Set up the dataset
    action_features = hw_to_dataset_features(robot.action_features, "action")  # type: ignore
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}
    dataset = LeRobotDataset.create(
        repo_id=f"avilay/{task}",
        fps=30,
        features=dataset_features,
        robot_type=robot.name,
        use_videos=True,
        image_writer_threads=4,
    )
    init_rerun(session_name="recording")

    robot.connect(calibrate=False)

    teleop_cfg = SO101LeaderConfig(port=YANTRA_TELEOP, id="yantra_teleop")
    teleop = SO101Leader(teleop_cfg)

    teleop_action_proc, robot_action_proc, robot_obs_proc = make_default_processors()

    for epidx in range(1, num_episodes + 1):
        log_say(f"Recording episode {epidx + 1} of {num_episodes}")
        record_loop(
            robot=robot,
            events={},
            fps=30,
            teleop_action_processor=teleop_action_proc,
            robot_action_processor=robot_action_proc,
            robot_observation_processor=robot_obs_proc,
            teleop=teleop,
            dataset=dataset,
            control_time_s=episode_time,
            single_task=task,
            display_data=True,
        )

        log_say("Rest the environment.")
        record_loop(
            robot=robot,
            events={},
            fps=30,
            teleop_action_processor=teleop_action_proc,
            robot_action_processor=robot_action_proc,
            robot_observation_processor=robot_obs_proc,
            teleop=teleop,
            control_time_s=reset_time,
            single_task=task,
            display_data=True,
        )

        dataset.save_episode()


if __name__ == "__main__":
    main()
