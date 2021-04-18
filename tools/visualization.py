import os
import numpy as np
import json
from wsrlib import pyart, radar2mat
from wsrdata.utils.bbox_utils import scale_XYWH_box
import matplotlib.pyplot as plt
import matplotlib.colors as pltc

# define which scans to visualize, which json to be the source of annotations
# SCAN_LIST_PATHS = {"train": os.path.join("../static/scan_lists/v0.0.1/train.txt"),
#                "test": os.path.join("../static/scan_lists/v0.0.1/test.txt")}
# JSON_PATH = "../datasets/roosts-v0.0.1-official/roosts-v0.0.1.json"
# OUTPUT_DIR = "../datasets/roosts-v0.0.1-official/visualization"
SCAN_LIST_PATHS = {pair: f"../static/scan_lists/v0.2.0/{pair}.txt" for pair in
               ['Ftian-KOKX', 'William Curran-KDOX', 'andrew-KAMX', 'andrew-KHGX', 'andrew-KJAX',
                'andrew-KLCH', 'andrew-KLIX', 'andrew-KMLB', 'andrew-KTBW', 'andrew-KTLH',
                'anon-KDOX', 'anon-KLIX', 'anon-KTBW', 'jafer1-KDOX', 'jafermjj-KDOX',
                'jberger1-KAMX', 'jberger1-KLIX', 'jberger1-KMLB', 'jberger1-KTBW', 'jpodrat-KLIX',
                'sheldon-KAMX', 'sheldon-KDOX', 'sheldon-KLIX', 'sheldon-KMLB', 'sheldon-KOKX',
                'sheldon-KRTX', 'sheldon-KTBW']
                   if os.path.exists(f"../static/scan_lists/v0.1.0/v0.1.0-subset-for-debugging/{pair}.txt")}
JSON_PATH = "../datasets/roosts-v0.1.0-official/roosts-v0.1.0.json"
OUTPUT_DIR = "../datasets/roosts-v0.1.0-official/visualization"

# visualization settings
COLOR_ARRAY = [
    '#006400', # for not scaled boxes
    '#FF00FF', # scaled to RCNN then to user factor 0.7429 which is sheldon average
    '#800080',
    '#FFA500',
    '#FFFF00'
]
NORMALIZERS = {
        'reflectivity':              pltc.Normalize(vmin=  -5, vmax= 35),
        'velocity':                  pltc.Normalize(vmin= -15, vmax= 15),
        'spectrum_width':            pltc.Normalize(vmin=   0, vmax= 10),
        'differential_reflectivity': pltc.Normalize(vmin=  -4, vmax= 8),
        'differential_phase':        pltc.Normalize(vmin=   0, vmax= 250),
        'cross_correlation_ratio':   pltc.Normalize(vmin=   0, vmax= 1.1)
}

# load data
with open(JSON_PATH, "r") as f:
    dataset = json.load(f)
scan_to_id = {}
for scan_list in dataset["scans"]:
    for scan in dataset["scans"][scan_list]:
        scan_to_id[scan["scan"]] = (scan_list, scan["scan_id"])
array_channel_indices = dataset["info"]["array_channel_indices"]

# plot
for scan_list in SCAN_LIST_PATHS:
    scans = [scan.strip() for scan in open(SCAN_LIST_PATHS[scan_list], "r").readlines()]

    for n, SCAN in enumerate(scans):
        print(f"Processing the {n+1}th scan")
        scan = dataset["scans"][scan_to_id[SCAN][0]][scan_to_id[SCAN][1]]
        array = np.load(os.path.join(dataset["info"]["array_dir"], scan["array_path"]))

        fig, axs = plt.subplots(1, 3, figsize=(21, 7), constrained_layout=True)
        for i, (attr, elev) in enumerate([("reflectivity", "0.5"), ("reflectivity", "1.5"), ("velocity", "0.5")]):
            subplt = axs[i]
            subplt.axis('off')
            subplt.set_title(f"{attr}, elev: {elev}", fontsize=18)
            cm = plt.get_cmap(pyart.config.get_field_colormap(attr))
            rgb = cm(NORMALIZERS[attr](array[array_channel_indices[attr][elev], :, :]))
            subplt.imshow(rgb)
            for annotation in scan["annotations"]:
                bbox = annotation["bbox"]
                # uncomment the following lines if the input bboxes contain annotator biases
                # subplt.add_patch(
                #     plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                #                   fill=False,
                #                   edgecolor=COLOR_ARRAY[0],
                #                   linewidth=1.2)
                # )
                # subplt.text(10, 10, 'not scaled',
                #             bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=COLOR_ARRAY[0])
                #
                # bbox = scale_XYWH_box(bbox, dataset["info"]["bbox_scaling_factors"][annotation["bbox_annotator"]])
                subplt.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3],
                                  fill=False,
                                  edgecolor=COLOR_ARRAY[1],
                                  linewidth=1.2)
                )
                subplt.text(10, 40, 'scaled -> RCNN -> sheldon average (0.7429)',
                            bbox=dict(facecolor='white', alpha=0.5), fontsize=14, color=COLOR_ARRAY[1])

        # save
        if not os.path.exists(OUTPUT_DIR): os.mkdir(OUTPUT_DIR)
        if not os.path.exists(os.path.join(OUTPUT_DIR, scan_list)): os.mkdir(os.path.join(OUTPUT_DIR, scan_list))
        fig.savefig(os.path.join(OUTPUT_DIR, scan_list, SCAN + ".png"), bbox_inches="tight")
        plt.close(fig)