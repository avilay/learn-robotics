import logging
import os
import readline  # noqa: F401
import time
from pathlib import Path

import click
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig
from matplotlib import pyplot as plt

logging.getLogger("draccus.parsers").setLevel(logging.ERROR)
logging.getLogger("qt.qpa.services").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.ERROR, handlers=(logging.StreamHandler(),), force=True
)

YANTRA_ROBOT = os.environ["YANTRA_ROBOT"]
YANTRA_TELEOP = os.environ["YANTRA_TELEOP"]
GRIPPER_CAMERA = Path(os.environ["YANTRA_GRIPPER_CAMERA"])
ENV_CAMERA = Path(os.environ["YANTRA_ENV_CAMERA"])


def build_lerp(init, final, tot_ticks):
    def lerp(tick):
        return (final - init) * tick / tot_ticks + init

    return lerp


def robot_wirecheck():
    print("\nCHECKING ROBOT")
    print("--------------")
    robot_cfg = SO101FollowerConfig(
        port=YANTRA_ROBOT,
        id="yantra_robot",
        cameras={
            "env": OpenCVCameraConfig(
                index_or_path=ENV_CAMERA, width=640, height=480, fps=30
            ),
            "gripper": OpenCVCameraConfig(
                index_or_path=GRIPPER_CAMERA, width=640, height=480, fps=30
            ),
        },
    )

    robot = SO101Follower(robot_cfg)
    robot.connect(calibrate=False)
    print(f"Is calibrated: {robot.is_calibrated}")
    print(f"Is connected: {robot.is_connected}")

    obs = robot.get_observation()
    print("Motor Positions:")
    print(f"\tShoulder Pan: {obs['shoulder_pan.pos']:.3f}")
    print(f"\tShoulder Lift: {obs['shoulder_lift.pos']:.3f}")
    print(f"\tElbow Flex: {obs['elbow_flex.pos']:.3f}")
    print(f"\tWrist Flex: {obs['wrist_flex.pos']:.3f}")
    print(f"\tWrist Roll: {obs['wrist_roll.pos']:.3f}")
    print(f"\tGripper: {obs['gripper.pos']:.3f}")
    plt.imshow(obs["gripper"])  # this img is already in RGB format
    plt.show()
    plt.imshow(obs["env"])
    plt.show()

    ans = input("Move the robot (y/N)?")
    if ans.lower() == "y":
        tot_ticks = 20
        shoulder_pan_lerp = build_lerp(
            obs["shoulder_pan.pos"], obs["shoulder_pan.pos"] - 5.0, tot_ticks
        )
        sleep_secs = 1 / tot_ticks
        for tick in range(1, tot_ticks + 1):
            robot.send_action({"shoulder_pan.pos": shoulder_pan_lerp(tick)})
            time.sleep(sleep_secs)
    else:
        print("Skipping moving check.")

    robot.disconnect()


def teleop_wirecheck():
    print("\nCHECKING TELEOP")
    print("---------------")
    teleop_cfg = SO101LeaderConfig(port=YANTRA_TELEOP, id="yantra_teleop")

    teleop = SO101Leader(teleop_cfg)
    teleop.connect(calibrate=False)
    print(f"Is calibrated: {teleop.is_calibrated}")
    print(f"Is connected: {teleop.is_connected}")

    action = teleop.get_action()
    print("Motor Positions:")
    print(f"\tShoulder Pan: {action['shoulder_pan.pos']:.3f}")
    print(f"\tShoulder Lift: {action['shoulder_lift.pos']:.3f}")
    print(f"\tElbow Flex: {action['elbow_flex.pos']:.3f}")
    print(f"\tWrist Flex: {action['wrist_flex.pos']:.3f}")
    print(f"\tWrist Roll: {action['wrist_roll.pos']:.3f}")
    print(f"\tGripper: {action['gripper.pos']:.3f}")

    teleop.disconnect()


@click.command()
@click.option(
    "--robot", "check_what", flag_value="only-robot", help="Wire check the robot."
)
@click.option(
    "--teleop", "check_what", flag_value="only-teleop", help="Wire check the teleop."
)
@click.option(
    "--both",
    "check_what",
    flag_value="both-robot-teleop",
    default=True,
    help="Wire check both the robot and the teleop.",
)
def main(check_what):
    print("ENVIRONMENT VARIABLES:")
    print("----------------------")
    print(f"YANTRA_ROBOT: {YANTRA_ROBOT}")
    print(f"YANTRA_TELEOP: {YANTRA_TELEOP}")
    print(f"YANTRA_GRIPPER_CAMERA: {GRIPPER_CAMERA}")
    print(f"YANTRA_ENV_CAMERA: {ENV_CAMERA}")

    try:
        if check_what == "only-robot":
            robot_wirecheck()
        elif check_what == "only-teleop":
            teleop_wirecheck()
        elif check_what == "both-robot-teleop":
            robot_wirecheck()
            teleop_wirecheck()
        else:
            raise RuntimeError(f"Unknown option - {check_what}!")
    except Exception as err:
        click.secho(f"ERROR: {err}", fg="red")


if __name__ == "__main__":
    main()
