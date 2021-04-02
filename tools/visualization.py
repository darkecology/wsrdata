import os
import numpy as np
import json
from wsrlib import pyart, radar2mat
import matplotlib.pyplot as plt
cm = plt.get_cmap('jet')

# define which scans to visualize, which json to be the source of annotations
SPLIT_PATHS = {"train": os.path.join("../static/splits/v0.1.0/train.txt"),
               "test": os.path.join("../static/splits/v0.1.0/test.txt")}
JSON_PATH = "../datasets/roosts-v0.1.0-official/roosts-v0.1.0.json"
OUTPUT_DIR = "../datasets/roosts-v0.1.0-official/visualization"

def scale(data, a, b):
    return np.clip((data - a)/(b-a), 0., 1.)

# set some a and b values for scaling
scale_clip = {"reflectivity": (-15, 30),
              "velocity": (-15, 15),
              "spectrum_width": (0, 8)}

# colors for bboxes
color_array = [
    '#FF00FF',  # for not scaled boxes
    '#006400',  # for scale strategy 1
    '#800080',
    '#FFA500',
    '#FFFF00'
]

# scale strategy 1: normalize to RCNN then to sheldon average
def scale_box_1(bbox, annotator_scale_factor):
    radius = [bbox[2] / 2, bbox[3] / 2]
    new_radius = [r / annotator_scale_factor * 0.7429 for r in radius]
    center = [(2 * bbox[0] + bbox[2] - 1) / 2, (2 * bbox[1] + bbox[3] - 1) / 2]

    new_left = int(center[0] - new_radius[0])
    new_right = center[0] * 2 - new_left
    new_top = int(center[1] - new_radius[1])
    new_bottom = center[1] * 2 - new_top
    return [new_left, new_top, new_right - new_left + 1, new_bottom - new_top + 1]

# load data
with open(JSON_PATH, "r") as f:
    dataset = json.load(f)
scan_to_id = {}
for split in dataset["scans"]:
    for scan in dataset["scans"][split]:
        scan_to_id[scan["scan"]] = scan["scan_id"]
array_channel_indices = dataset["info"]["array_channel_indices"]

# plot
for split in SPLIT_PATHS:
    scans = [scan.strip() for scan in open(SPLIT_PATHS[split], "r").readlines()]

    for SCAN in scans:
        scan = dataset["scans"][split][scan_to_id[SCAN]]
        array = np.load(scan["array_path"])

        fig, axs = plt.subplots(1, 3, figsize=(21, 7), constrained_layout=True)
        for i, (attr, elev) in enumerate([("reflectivity", "0.5"), ("reflectivity", "1.5"), ("velocity", "0.5")]):
            subplt = axs[i]
            subplt.axis('off')
            subplt.set_title(f"{attr}, elev: {elev}", fontsize=18)
            rgb = cm(scale(array[array_channel_indices[attr][elev], :, :],
                           scale_clip[attr][0],
                           scale_clip[attr][1]))
            subplt.imshow(rgb)
            for annotation in scan["annotations"]:
                bbox = annotation["bbox"]
                subplt.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                                  fill=False,
                                  edgecolor=color_array[0],
                                  linewidth=1.2)
                )
                subplt.text(10, 10, 'not scaled',
                            bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=color_array[0])

                bbox = scale_box_1(bbox, dataset["info"]["bbox_scaling_factors"][annotation["bbox_annotator"]])
                subplt.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                                  fill=False,
                                  edgecolor=color_array[1],
                                  linewidth=1.2)
                )
                subplt.text(10, 40, 'scaled -> RCNN -> sheldon average (0.7429)',
                            bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=color_array[1])

        # save
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        fig.savefig(os.path.join(OUTPUT_DIR, SCAN + ".png"))
        plt.close(fig)