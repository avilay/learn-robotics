from collections import namedtuple

import toga
from toga.constants import CENTER

from zeromode.utils import get_joint_limits

KeyLabel = namedtuple("KeyLabel", ["key", "label"])

joints = [
    KeyLabel("shoulder_pan", "Shoulder Pan"),
    KeyLabel("shoulder_lift", "Shoulder Lift"),
    KeyLabel("elbow_flex", "Elbow Flex"),
    KeyLabel("wrist_flex", "Wrist Flex"),
    KeyLabel("wrist_roll", "Wrist Roll"),
    KeyLabel("gripper", "Gripper"),
]

joint_limits = get_joint_limits()


def make_header(text: str) -> toga.Label:
    return toga.Label(text, font=("normal", "normal", "bold", 20, ["system"]))
    # return toga.Box(children=[])


def make_row(label: str, widget: toga.Widget) -> toga.Box:
    return toga.Box(
        children=[
            toga.Box(
                flex=1,
                children=[
                    toga.Label(label, flex=1),
                    widget,
                ],
                align_items=CENTER,
            )
        ]
    )


def make_input(joint: str) -> toga.NumberInput:
    return toga.NumberInput(
        min=joint_limits[joint][0],
        max=joint_limits[joint][1],
        step=0.1,
        flex=1,
    )
