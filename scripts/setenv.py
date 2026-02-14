from pathlib import Path

YANTRA_ROBOT_ID = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6054518-if00"
YANTRA_TELEOP_ID = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AE6054516-if00"
YANTRA_GRIPPER_CAMERA_ID = (
    "/dev/v4l/by-id/usb-GENERAL_GENERAL_WEBCAM_JH0319_20210712_v102-video-index0"
)
YANTRA_ENV_CAMERA_ID = "/dev/v4l/by-id/usb-046d_BRIO_301_2238CFA29DD8-video-index0"

yantra_robot = str(Path(YANTRA_ROBOT_ID).resolve())
yantra_teleop = str(Path(YANTRA_TELEOP_ID).resolve())
yantra_gripper_camera = str(Path(YANTRA_GRIPPER_CAMERA_ID).resolve())
yantra_env_camera = str(Path(YANTRA_ENV_CAMERA_ID).resolve())

# Setting global environment variables so that I can use this inside a fish
# function.
print(f"set -gx YANTRA_ROBOT '{yantra_robot}'")
print(f"set -gx YANTRA_TELEOP '{yantra_teleop}'")
print(f"set -gx YANTRA_GRIPPER_CAMERA '{yantra_gripper_camera}'")
print(f"set -gx YANTRA_ENV_CAMERA '{yantra_env_camera}'")
