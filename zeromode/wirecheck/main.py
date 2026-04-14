import toga

from zeromode.wirecheck.robot_panel import RobotPanel
from zeromode.wirecheck.teleop_panel import TeleopPanel


class Wirecheck(toga.App):
    def __init__(self, formal_name: str, app_id: str) -> None:
        super().__init__(formal_name, app_id)
        self.robot_panel = RobotPanel()
        self.teleop_panel = TeleopPanel()

    def startup(self) -> None:
        self.main_window: toga.MainWindow = toga.MainWindow(
            title="Wirecheck", size=(1000, 500)
        )
        self.commands.add(*self.robot_panel.commands)
        self.commands.add(*self.teleop_panel.commands)
        rootbox = toga.Box(
            children=[self.robot_panel.make_box(), self.teleop_panel.make_box()],
            flex=1,
            margin=20,
        )
        self.main_window.content = rootbox
        self.main_window.show()


def main():
    # toga.Widget.DEBUG_LAYOUT_ENABLED = True  # type: ignore
    app = Wirecheck("Wirecheck", "dev.zeromode.wirecheck")
    app.main_loop()


if __name__ == "__main__":
    main()
