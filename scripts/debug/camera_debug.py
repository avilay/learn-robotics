import logging
import time
from pathlib import Path

import click
import cv2
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from matplotlib import pyplot as plt

logging.basicConfig(level=logging.WARNING)
logging.warning("TEST WARNING")


def using_opencv_api(port):
    print(f"\nChecking port {port}")
    vc0 = cv2.VideoCapture(port, 0)
    vc0.set(cv2.CAP_PROP_FRAME_WIDTH, float(640))
    vc0.set(cv2.CAP_PROP_FRAME_HEIGHT, float(480))
    vc0.set(cv2.CAP_PROP_FPS, float(30))
    ret, frame = vc0.read()
    if ret is None or frame is None:
        print("ERROR")
    else:
        print("Seems to work fine!")
        # OpenCV captures frames in BGR format, but plt.imshow() expects RGB.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        plt.imshow(frame_rgb)
        plt.show()
    vc0.release()


def using_lerobot_api(port):
    print(f"\nChecking port {port}")

    cfg0 = OpenCVCameraConfig(index_or_path=Path(port), fps=30, width=640, height=480)
    cam0 = OpenCVCamera(cfg0)
    cam0.connect(warmup=False)
    time.sleep(1)
    print("Seems to work fine!")
    # frame = cam0.async_read()
    frame = cam0.read()
    plt.imshow(frame)
    plt.show()

    cam0.disconnect()


@click.command()
@click.option("--opencv", "api", flag_value="opencv", help="Use the opencv API.")
@click.option("--lerobot", "api", flag_value="lerobot", help="Use the lerobot API.")
@click.argument("camera")
def main(api, camera):
    if api == "opencv":
        using_opencv_api(camera)
    elif api == "lerobot":
        using_lerobot_api(camera)
    else:
        raise RuntimeError("KA-BOOM!!")


if __name__ == "__main__":
    main()
