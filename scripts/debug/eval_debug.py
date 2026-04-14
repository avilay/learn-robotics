import os
import time
from pathlib import Path

import numpy as np
import torch
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.utils.control_utils import predict_action, prepare_observation_for_inference
from typing import cast

rng = np.random.default_rng()

policy = ACTPolicy.from_pretrained("avilay/pick_and_place_v1.0.0")

policy_preproc, policy_postproc = make_pre_post_processors(
    policy_cfg=policy,  # type: ignore
    pretrained_path="avilay/pick_and_place_v1.0.0",
    preprocessor_overrides={"device_processor": {"device": "cpu"}},
    postprocessor_overrides={"device_processor": {"device": "cpu"}},
)

policy.reset()
policy_preproc.reset()
policy_postproc.reset()

obs = {
    "shoulder_pan.pos": 0.6593406593406593,
    "shoulder_lift.pos": -105.18681318681318,
    "elbow_flex.pos": 98.1978021978022,
    "wrist_flex.pos": 59.16483516483517,
    "wrist_roll.pos": -3.208791208791209,
    "gripper.pos": 0.6816632583503749,
    "gripper": rng.integers(low=0, high=256, size=(480, 640, 3)),
    "env": rng.integers(low=0, high=256, size=(480, 640, 3)),
}

obs_df: dict[str, np.ndarray] = {
    "observation.state": np.array(
        [
            obs["shoulder_pan.pos"],
            obs["shoulder_lift.pos"],
            obs["elbow_flex.pos"],
            obs["wrist_flex.pos"],
            obs["wrist_roll.pos"],
            obs["gripper.pos"],
        ],
        dtype=np.float32,
    ),
    "observation.images.gripper": cast(np.ndarray, obs["gripper"]),
    "observation.images.env": cast(np.ndarray, obs["env"]),
}

cpu = torch.device("cpu")

# next_action = predict_action(
#     observation=obs_df,
#     policy=policy,
#     device=cpu,
#     preprocessor=policy_preproc,
#     postprocessor=policy_postproc,
#     use_amp=policy.config.use_amp,
#     task="eval_pick_and_place_v1.0.0",
#     robot_type="so_follower",
# )

with torch.inference_mode():
    obs_df = prepare_observation_for_inference(obs_df, cpu, "eval_pick_and_place", "so_follower")
    input_obs = policy_preproc(obs_df)
    output_action = policy.select_action(input_obs)
    next_action = policy_postproc(output_action)

print(type(next_action), next_action.shape, next_action.dtype)
