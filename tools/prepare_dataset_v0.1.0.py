import os
import json

version = "v0.1.0"
split_version = "v0.1.0"
split_paths = {"train": os.path.join("../splits", split_version, "train.txt"),
          "test": os.path.join("../splits", split_version, "test.txt")}
annotation_version = "v0.1.0"


info = {
    "description": "A mini roost dataset with bbox annotations for testing whether "
                   "the data preparation pipeline is succesfully set up",
    "url": "",
    "version": version,
    "split_version": split_version,
    "annotation_version": annotation_version,
    "data_created": "2021/03/15",
    "array_shapes": [(600, 600, 15)],
    "channels": [(property, i) for property in ["reflectivity", "radial_velocity", "spectrum_width"]
                 for i in [0.5, 1.0, 1.5, 2.0, 2.5]]
}

array = {
    "id": int,
    "path": str,
    "license_id": int,
    "scan": str,
    "array_shape_id": int,
}

annotation = {
    "id": int,
    "array_id": int,
    "category_id": int,
    "bbox": [x, y, width, height],
    "bbox_annotator": str,
    "bbox_scaling_factor": float,
    "segmentation": [polygon],
    "segmentation_annotator": str,
}

dataset = {
    "info": info,
    "license": [],
    "arrays": {"train": [array],
               "val": [array],
               "test": [array]},
    "categories": ["roost"],
    "annotations": {"train": [annotation],
                    "val": [annotation],
                    "test": [annotation]},
}

with open("../datasets/roosts-" + version + ".json", 'w') as f:
    json.dump(dataset, f)