import toga
from toga.constants import CENTER, COLUMN, END

from zeromode.wirecheck.widgets import make_header, make_input, make_row


class RobotPanel:
    def __init__(self) -> None:
        self.shoulder_pan_input = make_input("shoulder_pan")
        self.shoulder_lift_input = make_input("shoulder_lift")
        self.elbow_flex_input = make_input("elbow_flex")
        self.wrist_flex_input = make_input("wrist_flex")
        self.wrist_roll_input = make_input("wrist_roll")
        self.gripper_input = toga.NumberInput(min=0, max=100, step=0.1, flex=1)
        self.gripper_img = toga.ImageView(
            toga.Image(src="placeholder.png"), width=320, height=240
        )
        self.env_img = toga.ImageView(
            toga.Image(src="placeholder.png"), width=320, height=240
        )

        self.live_feed_switch = toga.Switch("Live Feed")

        # Disable everything until the robot is connected
        self.shoulder_pan_input.enabled = False
        self.shoulder_lift_input.enabled = False
        self.elbow_flex_input.enabled = False
        self.wrist_flex_input.enabled = False
        self.wrist_roll_input.enabled = False
        self.gripper_input.enabled = False
        self.live_feed_switch.enabled = False

        group = toga.Group("Robot")
        self.connect_cmd = toga.Command(
            self.connect,
            text="Connect",
            tooltip="Connect the robot",
            group=group,
            order=1,
        )
        self.disconnect_cmd = toga.Command(
            self.disconnect,
            text="Disconnect",
            tooltip="Disconnect robot",
            group=group,
            order=2,
            enabled=False,
        )
        self.commands = [self.connect_cmd, self.disconnect_cmd]

        self.get_observation_btn = toga.Button(
            "Get Observation", on_press=self.get_observation, width=150, enabled=False
        )
        self.send_action_btn = toga.Button(
            "Send Action", on_press=self.send_action, width=150, enabled=False
        )

    def make_box(self) -> toga.Box:
        box = toga.Box(direction=COLUMN, flex=1, gap=5)
        box.add(
            toga.Box(
                children=[
                    make_header("Robot"),
                    toga.Box(
                        children=[self.live_feed_switch], justify_content=END, flex=1
                    ),
                ],
                align_items=CENTER,
            )
        )
        box.add(make_row("Shoulder Pan", self.shoulder_pan_input))
        box.add(make_row("Shoulder Lift", self.shoulder_lift_input))
        box.add(make_row("Elbow Flex", self.elbow_flex_input))
        box.add(make_row("Wrist Flex", self.wrist_flex_input))
        box.add(make_row("Wrist Roll", self.wrist_roll_input))
        box.add(make_row("Gripper", self.gripper_input))
        box.add(toga.Box(children=[self.env_img, self.gripper_img], gap=3))
        box.add(
            toga.Box(
                children=[
                    self.get_observation_btn,
                    self.send_action_btn,
                ],
                margin_top=7,
                gap=3,
            )
        )
        return box

    def connect(self, command: toga.Command, **kwargs) -> bool:
        self.shoulder_pan_input.enabled = True
        self.shoulder_lift_input.enabled = True
        self.elbow_flex_input.enabled = True
        self.wrist_flex_input.enabled = True
        self.wrist_roll_input.enabled = True
        self.gripper_input.enabled = True
        self.live_feed_switch.enabled = True
        self.disconnect_cmd.enabled = True
        self.get_observation_btn.enabled = True
        self.send_action_btn.enabled = True
        command.enabled = False
        return True

    def disconnect(self, command: toga.Command, **kwargs) -> bool:
        self.shoulder_pan_input.enabled = False
        self.shoulder_lift_input.enabled = False
        self.elbow_flex_input.enabled = False
        self.wrist_flex_input.enabled = False
        self.wrist_roll_input.enabled = False
        self.gripper_input.enabled = False
        self.live_feed_switch.enabled = False
        self.get_observation_btn.enabled = False
        self.send_action_btn.enabled = False
        self.connect_cmd.enabled = True
        command.enabled = False
        return True

    def get_observation(self, button: toga.Button) -> None:
        pass

    def send_action(self, button: toga.Button) -> None:
        pass
