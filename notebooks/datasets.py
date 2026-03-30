import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import torch
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    import numpy as np
    import matplotlib.pyplot as plt

    return LeRobotDataset, np, plt


@app.cell
def _():
    # This will look for this repo in the local cache at:
    # ~/.cache/huggingface/lerobot/avilay/pick_and_place_50/
    repoid = "avilay/pick_and_place_50"
    return (repoid,)


@app.cell
def _(LeRobotDataset, repoid):
    dataset = LeRobotDataset(repoid)
    len(dataset)
    return (dataset,)


@app.cell
def _(dataset):
    sample = dataset[100]
    sample
    return (sample,)


@app.cell
def _(sample):
    sample["observation.images.env"].shape
    return


@app.cell
def _(np, plt, sample):
    # PyTorch images are channel-first (C, H, W), I need to make it channel-last (H, W, C) before
    # matplotlib can plot it.
    envimg = np.transpose(sample["observation.images.env"].numpy(), (1, 2, 0))
    plt.imshow(envimg)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
