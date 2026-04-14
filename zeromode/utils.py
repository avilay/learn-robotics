import json
import time
from pathlib import Path

import numpy as np

# Lets move 30 steps per second in keeping with the default 30 FPS.
FPS = 30

reset_pos = {
    "shoulder_pan.pos": 0.6593406593406593,
    "shoulder_lift.pos": -105.18681318681318,
    "elbow_flex.pos": 98.1978021978022,
    "wrist_flex.pos": 59.16483516483517,
    "wrist_roll.pos": -3.208791208791209,
    "gripper.pos": 0.6816632583503749,
}


def ticks(frames_per_sec: int, duration_secs: int):
    tot_ticks = frames_per_sec * duration_secs
    tick_duration = 1 / frames_per_sec
    for tick in range(tot_ticks):
        start = time.perf_counter()

        yield tick

        elapsed = time.perf_counter() - start
        remaining = tick_duration - elapsed
        if remaining > 0:
            time.sleep(remaining)


def build_lerp(init, final, tot_ticks):
    def lerp(tick):
        return (final - init) * tick / tot_ticks + init

    return lerp


def reset_robot_pos(robot):
    obs = robot.get_observation()
    initpos = np.array(
        [
            obs["shoulder_pan.pos"],
            obs["shoulder_lift.pos"],
            obs["elbow_flex.pos"],
            obs["wrist_flex.pos"],
            obs["wrist_roll.pos"],
            obs["gripper.pos"],
        ]
    )
    finalpos = np.array(
        [
            reset_pos["shoulder_pan.pos"],
            reset_pos["shoulder_lift.pos"],
            reset_pos["elbow_flex.pos"],
            reset_pos["wrist_flex.pos"],
            reset_pos["wrist_roll.pos"],
            reset_pos["gripper.pos"],
        ]
    )

    # sleep_secs = 1 / FPS

    # Lets take 2 seconds to get the robot back into its reset pos.
    # TODO: Calculate this based on the robot's current position.
    tot_seconds = 2

    tot_ticks = tot_seconds * FPS
    poslerp = build_lerp(initpos, finalpos, tot_ticks)

    for tick in ticks(FPS, tot_seconds):
        newpos = poslerp(tick)
        robot.send_action(
            {
                "shoulder_pan.pos": newpos[0],
                "shoulder_lift.pos": newpos[1],
                "elbow_flex.pos": newpos[2],
                "wrist_flex.pos": newpos[3],
                "wrist_roll.pos": newpos[4],
                "gripper.pos": newpos[5],
            }
        )


def get_joint_limits() -> dict[str, tuple[float, float]]:
    # Load the calibration data
    cali_file = (
        Path.home()
        / ".cache"
        / "huggingface"
        / "lerobot"
        / "calibration"
        / "robots"
        / "so_follower"
        / "yantra_robot.json"
    )
    with open(cali_file, "rt") as fin:
        cali = json.load(fin)

    limits: dict[str, tuple[float, float]] = {}
    for joint in (
        "shoulder_pan",
        "shoulder_lift",
        "elbow_flex",
        "wrist_flex",
        "wrist_roll",
    ):
        range_min = cali[joint]["range_min"]
        range_max = cali[joint]["range_max"]
        mid = (range_max - range_min) / 2
        deg_max = mid * 360 / 4096
        deg_min = -deg_max
        limits[joint] = (deg_min, deg_max)
    limits["gripper"] = (0, 100)

    return limits
