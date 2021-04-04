import os
import numpy as np
import json
from wsrlib import pyart, radar2mat
from wsrdata.utils.bbox_utils import scale_XYWH_box
import matplotlib.pyplot as plt
cm = plt.get_cmap('jet')

# define which scans to visualize, which json to be the source of annotations
# SPLIT_PATHS = {"train": os.path.join("../static/splits/v0.1.0/train.txt"),
#                "test": os.path.join("../static/splits/v0.1.0/test.txt")}
# JSON_PATH = "../datasets/roosts-v0.1.0-official/roosts-v0.1.0.json"
# OUTPUT_DIR = "../datasets/roosts-v0.1.0-official/visualization"
SPLIT_PATHS = {pair: f"../static/splits/v0.2.0/{pair}.txt" for pair in
               ['Ftian-KOKX', 'William Curran-KDOX', 'andrew-KAMX', 'andrew-KHGX', 'andrew-KJAX',
                'andrew-KLCH', 'andrew-KLIX', 'andrew-KMLB', 'andrew-KTBW', 'andrew-KTLH',
                'anon-KDOX', 'anon-KLIX', 'anon-KTBW', 'jafer1-KDOX', 'jafermjj-KDOX',
                'jberger1-KAMX', 'jberger1-KLIX', 'jberger1-KMLB', 'jberger1-KTBW', 'jpodrat-KLIX',
                'sheldon-KAMX', 'sheldon-KDOX', 'sheldon-KLIX', 'sheldon-KMLB', 'sheldon-KOKX',
                'sheldon-KRTX', 'sheldon-KTBW'] if os.path.exists(f"../static/splits/v0.2.0/{pair}.txt")}
JSON_PATH = "../datasets/roosts-v1.0.0-official/roosts-v1.0.0.json"
OUTPUT_DIR = "../datasets/roosts-v1.0.0-official/visualization"

def scale(data, a, b):
    return np.clip((data - a)/(b-a), 0., 1.)

# set some a and b values for scaling
scale_clip = {"reflectivity": (-15, 30),
              "velocity": (-15, 15),
              "spectrum_width": (0, 8)}

# colors for bboxes
color_array = [
    '#006400', # for not scaled boxes
    '#FF00FF', # scaled to RCNN then to user factor 0.7429 which is sheldon average
    '#800080',
    '#FFA500',
    '#FFFF00'
]

# load data
with open(JSON_PATH, "r") as f:
    dataset = json.load(f)
scan_to_id = {}
for split in dataset["scans"]:
    for scan in dataset["scans"][split]:
        scan_to_id[scan["scan"]] = (split, scan["scan_id"])
array_channel_indices = dataset["info"]["array_channel_indices"]

# plot
for split in SPLIT_PATHS:
    scans = [scan.strip() for scan in open(SPLIT_PATHS[split], "r").readlines()]

    for n, SCAN in enumerate(scans):
        print(f"Processing the {n+1}th scan")
        scan = dataset["scans"][scan_to_id[SCAN][0]][scan_to_id[SCAN][1]]
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
                # uncomment the following lines if the input bboxes contain annotator biases
                # subplt.add_patch(
                #     plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                #                   fill=False,
                #                   edgecolor=color_array[0],
                #                   linewidth=1.2)
                # )
                # subplt.text(10, 10, 'not scaled',
                #             bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=color_array[0])
                #
                # bbox = scale_XYWH_box(bbox, dataset["info"]["bbox_scaling_factors"][annotation["bbox_annotator"]])
                subplt.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                                  fill=False,
                                  edgecolor=color_array[1],
                                  linewidth=1.2)
                )
                subplt.text(10, 40, 'scaled -> RCNN -> sheldon average (0.7429)',
                            bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=color_array[1])

        # save
        if not os.path.exists(OUTPUT_DIR): os.mkdir(OUTPUT_DIR)
        if not os.path.exists(os.path.join(OUTPUT_DIR, split)): os.mkdir(os.path.join(OUTPUT_DIR, split))
        fig.savefig(os.path.join(OUTPUT_DIR, split, SCAN + ".png"), bbox_inches="tight")
        plt.close(fig)