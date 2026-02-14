from pathlib import Path

import click
import cv2
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from matplotlib import pyplot as plt

# RESOLVED: The problem was that I was running both the cameras through the same USB port via a USB
# hub and therefore ran into a resource limitation issue. After connecting the cameras to different
# physical USB ports, everything started working.
# For now both the robots are on USB2, the gripper cam is also on USB2, the env cam only has a USB-C
# port, so it is using that.

def using_opencv_api(ports):
    print(f"\nChecking port {ports[0]}")
    vc0 = cv2.VideoCapture(ports[0], 0)
    vc0.set(cv2.CAP_PROP_FRAME_WIDTH, float(640))
    vc0.set(cv2.CAP_PROP_FRAME_HEIGHT, float(480))
    vc0.set(cv2.CAP_PROP_FPS, float(30))
    ret, frame = vc0.read()
    if ret is None or frame is None:
        print("ERROR")
    else:
        print("Seems to work fine!")
        plt.imshow(frame)
        plt.show()

    print(f"\nChecking port {ports[1]}")
    vc1 = cv2.VideoCapture(ports[1], 0)
    vc1.set(cv2.CAP_PROP_FRAME_WIDTH, float(640))
    vc1.set(cv2.CAP_PROP_FRAME_HEIGHT, float(480))
    vc1.set(cv2.CAP_PROP_FPS, float(30))
    ret, frame = vc1.read()
    if ret is None or frame is None:
        print("ERROR")
    else:
        print("Seems to work fine!")
        plt.imshow(frame)
        plt.show()

    vc0.release()
    vc1.release()


def using_lerobot_api(ports):
    print(f"\nChecking port {ports[0]}")

    cfg0 = OpenCVCameraConfig(
        index_or_path=Path(ports[0]), fps=30, width=640, height=480
    )
    cam0 = OpenCVCamera(cfg0)
    cam0.connect()
    print("Seems to work fine!")
    frame = cam0.async_read()
    plt.imshow(frame)
    plt.show()

    cfg1 = OpenCVCameraConfig(
        index_or_path=Path(ports[1]), fps=30, width=640, height=480
    )
    cam1 = OpenCVCamera(cfg1)
    cam1.connect()
    print("Seems to work fine!")
    frame = cam1.async_read()
    plt.imshow(frame)
    plt.show()

    cam0.disconnect()
    cam1.disconnect()


@click.command()
@click.option("--opencv", "api", flag_value="opencv", help="Use the opencv API.")
@click.option("--lerobot", "api", flag_value="lerobot", help="Use the lerobot API.")
@click.option("--camera1", default="/dev/video0", help="The first camera to connect.")
@click.option("--camera2", default="/dev/video50", help="The second camera to connect.")
def main(api, camera1, camera2):
    """
    App to repro the camera bug.

    If the OpenCV APIs are used directly, both cameras will work fine. However, if LeRobot APIs are
    used, the second camera will always fail, does not matter which camera it is. By default the
    first camera (camera1) is set to /dev/video0 and the second camera (camera2) is set to
    /dev/video50. These values can be changed by the setting the appropriate options.
    """
    if api == "opencv":
        using_opencv_api((camera1, camera2))
    elif api == "lerobot":
        using_lerobot_api((camera1, camera2))
    else:
        raise RuntimeError("KA-BOOM!!")


if __name__ == "__main__":
    main()
    main()
    main()
