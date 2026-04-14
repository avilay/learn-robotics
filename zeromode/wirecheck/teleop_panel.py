import toga
from toga.constants import COLUMN, START

from zeromode.wirecheck.widgets import make_header, make_row


class TeleopPanel:
    def __init__(self):
        self.shoulder_pan_value = toga.Label("0", flex=1)
        self.shoulder_lift_value = toga.Label("0", flex=1)
        self.elbow_flex_value = toga.Label("0", flex=1)
        self.wrist_flex_value = toga.Label("0", flex=1)
        self.wrist_roll_value = toga.Label("0", flex=1)
        self.gripper_value = toga.Label("0", flex=1)

        group = toga.Group("Teleop")
        self.connect_cmd = toga.Command(
            self.connect,
            text="Connect",
            tooltip="Connect the teleop",
            group=group,
            order=1,
        )
        self.disconnect_cmd = toga.Command(
            self.disconnect,
            text="Disconnect",
            tooltip="Disconnect the teleop",
            group=group,
            order=2,
        )
        self.commands = [self.connect_cmd, self.disconnect_cmd]

    def make_box(self) -> toga.Box:
        box = toga.Box(direction=COLUMN, flex=1, gap=5)
        box.add(make_header("Teleop"))
        box.add(make_row("Shoulder Pan", self.shoulder_pan_value))
        box.add(make_row("Shoulder Lift", self.shoulder_lift_value))
        box.add(make_row("Elbow Flex", self.elbow_flex_value))
        box.add(make_row("Wrist Flex", self.wrist_flex_value))
        box.add(make_row("Gripper", self.gripper_value))
        box.add(
            toga.Box(
                children=[toga.Button("Get Action", on_press=self.get_action)],
                justify_content=START,
                margin_top=7,
            )
        )
        return box

    def connect(self, command: toga.Command, **kwargs) -> bool:
        return True

    def disconnect(self, command: toga.Command, **kwargs) -> bool:
        return True

    def get_action(self, button: toga.Button) -> None:
        pass
