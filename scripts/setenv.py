from pathlib import Path

ZEROMODE_ROBOT_ID = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6054518-if00"
ZEROMODE_TELEOP_ID = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6054516-if00"
ZEROMODE_GRIPPER_CAMERA_ID = (
    "/dev/v4l/by-id/usb-GENERAL_GENERAL_WEBCAM_JH0319_20210712_v102-video-index0"
)
ZEROMODE_ENV_CAMERA_ID = "/dev/v4l/by-id/usb-046d_BRIO_301_2238CFA29DD8-video-index0"

zeromode_robot = str(Path(ZEROMODE_ROBOT_ID).resolve())
zeromode_teleop = str(Path(ZEROMODE_TELEOP_ID).resolve())
zeromode_gripper_camera = str(Path(ZEROMODE_GRIPPER_CAMERA_ID).resolve())
zeromode_env_camera = str(Path(ZEROMODE_ENV_CAMERA_ID).resolve())

# Setting global environment variables so that I can use this inside a fish
# function.
print(f"set -gx ZEROMODE_ROBOT '{zeromode_robot}'")
print(f"set -gx ZEROMODE_TELEOP '{zeromode_teleop}'")
print(f"set -gx ZEROMODE_GRIPPER_CAMERA '{zeromode_gripper_camera}'")
print(f"set -gx ZEROMODE_ENV_CAMERA '{zeromode_env_camera}'")
