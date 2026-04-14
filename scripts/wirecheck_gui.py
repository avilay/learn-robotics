import asyncio

import toga
from toga.constants import CENTER, COLUMN, END

from zeromode.utils import get_joint_limits


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


class Wirecheck(toga.App):
    def __init__(self, formal_name: str, app_id: str) -> None:
        super().__init__(formal_name, app_id)

        joint_limits = get_joint_limits()

        self.shoulder_pan_input = toga.NumberInput(
            min=joint_limits["shoulder_pan"][0],
            max=joint_limits["shoulder_pan"][1],
            step=0.1,
        )
        self.shoulder_lift_input = toga.NumberInput(
            min=joint_limits["shoulder_lift"][0],
            max=joint_limits["shoulder_lift"][1],
            step=0.1,
            flex=1,
        )
        self.elbow_flex_input = toga.NumberInput(
            min=joint_limits["elbow_flex"][0],
            max=joint_limits["elbow_flex"][1],
            step=0.1,
            flex=1,
        )
        self.wrist_flex_input = toga.NumberInput(
            min=joint_limits["wrist_flex"][0],
            max=joint_limits["wrist_flex"][1],
            step=0.1,
            flex=1,
        )
        self.wrist_roll_input = toga.NumberInput(
            min=joint_limits["wrist_roll"][0],
            max=joint_limits["wrist_roll"][1],
            step=0.1,
            flex=1,
        )
        self.gripper_input = toga.NumberInput(min=0, max=100, step=0.1)
        self.gripper_img = toga.ImageView(
            toga.Image(src="placeholder.png"), width=320, height=240
        )
        self.env_img = toga.ImageView(
            toga.Image(src="placeholder.png"), width=320, height=240
        )

        self.shoulder_pan_value = toga.Label("0", flex=1)
        self.shoulder_lift_value = toga.Label("0", flex=1)
        self.elbow_flex_value = toga.Label("0", flex=1)
        self.wrist_flex_value = toga.Label("0", flex=1)
        self.wrist_roll_value = toga.Label("0", flex=1)
        self.gripper_value = toga.Label("0", flex=1)

        self.robot_btn = toga.Button(
            "Robot", font=("normal", "normal", "bold", 20, ["system"]), color="red"
        )
        self.robot_connect_switch = toga.Switch("Connect")
        self.robot_live_feed_switch = toga.Switch("Live Feed")
        robot_cmds = toga.Group("Robot")
        self.robot_connect_cmd = toga.Command(
            self.robot_connect,
            text="Connect",
            tooltip="Connect the robot",
            group=robot_cmds,
            order=1,
        )
        self.robot_get_obs_cmd = toga.Command(
            self.robot_get_obs,
            text="Get Observation",
            tooltip="Get single observation",
            group=robot_cmds,
            order=2,
            enabled=False,
        )
        self.robot_send_action_cmd = toga.Command(
            self.robot_send_action,
            text="Send Action",
            tooltip="Move the robot",
            group=robot_cmds,
            order=3,
            enabled=False,
        )
        self.robot_start_live_feed_cmd = toga.Command(
            self.robot_start_live_feed,
            text="Start Live Feed",
            tooltip="Get a live feed from the robot",
            group=robot_cmds,
            order=4,
            enabled=False,
        )
        self.robot_stop_live_feed_cmd = toga.Command(
            self.robot_stop_live_feed,
            text="Stop Life Feed",
            tooltip="Stop the robot live feed",
            group=robot_cmds,
            order=5,
            enabled=False,
        )
        self.robot_disconnect_cmd = toga.Command(
            self.robot_disconnect,
            text="Disconnect",
            tooltip="Disconnect the robot",
            group=robot_cmds,
            order=6,
            enabled=False,
        )
        self.robot_dbg_cmd = toga.Command(
            self.debug, text="Debug", group=robot_cmds, order=7
        )

        self.teleop_btn = toga.Button(
            "Teleop", font=("normal", "normal", "bold", 20, ["system"]), color="red"
        )
        teleop_cmds = toga.Group("Teleop")
        self.teleop_connect_cmd = toga.Command(
            self.teleop_connect,
            text="Connect",
            tooltip="Connect the teleop",
            group=teleop_cmds,
            order=1,
        )
        self.teleop_get_action_cmd = toga.Command(
            self.teleop_get_action,
            text="Get Action",
            tooltip="Get teleop action",
            group=teleop_cmds,
            order=2,
        )
        self.teleop_disconnect_cmd = toga.Command(
            self.teleop_disconnect,
            text="Disconnect",
            tooltip="Disconnect the teleop",
            group=teleop_cmds,
            order=3,
            enabled=False,
        )

    def startup(self):
        self.main_window: toga.MainWindow = toga.MainWindow(
            title="Wirecheck", size=(1000, 500)
        )

        self.commands.add(
            self.robot_connect_cmd,
            self.robot_get_obs_cmd,
            self.robot_send_action_cmd,
            self.robot_start_live_feed_cmd,
            self.robot_stop_live_feed_cmd,
            self.robot_disconnect_cmd,
            self.robot_dbg_cmd,
            self.teleop_connect_cmd,
            self.teleop_get_action_cmd,
            self.teleop_disconnect_cmd,
        )

        self.robot_connect_switch.margin_top = 3
        robot_box = toga.Box(
            direction=COLUMN,
            children=[
                toga.Box(
                    children=[
                        make_header("Robot"),
                        toga.Box(
                            children=[self.robot_live_feed_switch],
                            justify_content=END,
                            flex=1,
                        ),
                    ],
                    align_items=CENTER,
                ),
                make_row("Shoulder Pan", self.shoulder_pan_input),
                make_row("Shoulder Lift", self.shoulder_lift_input),
                make_row("Elbow Flex", self.elbow_flex_input),
                make_row("Wrist Flex", self.wrist_flex_input),
                make_row("Wrist Roll", self.wrist_roll_input),
                make_row("Gripper", self.gripper_input),
                toga.Box(children=[self.env_img, self.gripper_img], gap=3),
            ],
            flex=1,
            gap=5,
        )

        teleop_box = toga.Box(
            direction=COLUMN,
            children=[
                make_header("Teleop"),
                make_row("Shoulder Pan", self.shoulder_pan_value),
                make_row("Shoulder Lift", self.shoulder_lift_value),
                make_row("Elbow Flex", self.elbow_flex_value),
                make_row("Wrist Flex", self.wrist_flex_value),
                make_row("Wrist Roll", self.wrist_roll_value),
                make_row("Gripper", self.gripper_value),
            ],
            flex=1,
            gap=5,
        )

        rootbox = toga.Box(children=[robot_box, teleop_box], flex=1, margin=20)

        self.main_window.content = rootbox
        self.main_window.show()

    def robot_connect(self, command: toga.Command, **kwargs) -> bool:
        print(f"{command.text}: Connecting robot")
        self.robot_get_obs_cmd.enabled = True
        self.robot_send_action_cmd.enabled = True
        self.robot_start_live_feed_cmd.enabled = True
        # stop_live_feed will only be enabled once a live feed has been started
        self.robot_disconnect_cmd.enabled = True
        command.enabled = False
        return True

    def robot_get_obs(self, command: toga.Command, **kwargs) -> bool:
        return True

    def robot_send_action(self, command: toga.Command, **kwargs) -> bool:
        return True

    def robot_start_live_feed(self, command: toga.Command, **kwargs) -> bool:
        self.robot_stop_live_feed_cmd.enabled = True
        command.enabled = False
        return True

    def robot_stop_live_feed(self, command: toga.Command, **kwargs) -> bool:
        return True

    def robot_disconnect(self, command: toga.Command, **kwargs) -> bool:
        print(f"{command.text}: Disconnecting robot")
        if self.robot_stop_live_feed_cmd.enabled:
            print("Live feed is on")
            info = toga.InfoDialog(
                "Error", "Stop the live feed first before disconnecting!"
            )
            asyncio.create_task(self.main_window.dialog(info))
            return False
        self.robot_connect_cmd.enabled = True
        self.robot_get_obs_cmd.enabled = False
        self.robot_send_action_cmd.enabled = False
        self.robot_start_live_feed_cmd.enabled = False
        # stop_live_feed will only be enabled once a live feed has been started
        command.enabled = False
        return True

    def teleop_connect(self, command: toga.Command, **kwargs) -> bool:
        return True

    def teleop_get_action(self, command: toga.Command, **kwargs) -> bool:
        return True

    def teleop_disconnect(self, command: toga.Command, **kwargs) -> bool:
        return True

    def debug(self, command: toga.Command, **kwargs) -> bool:
        return True


if __name__ == "__main__":
    # toga.Widget.DEBUG_LAYOUT_ENABLED = True  # type: ignore
    app = Wirecheck("Wirecheck", "dev.zeromode.wirecheck")
    app.main_loop()
