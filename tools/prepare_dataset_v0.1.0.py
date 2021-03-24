"""
This script runs the data preparation pipeline to create the toy dataset v0.1.0.
It can be modified to create customized datasets.

In most cases, changing values for VARIABLEs in Step 1 suffices.
Use empty lists, empty strings, and -1 to fill fields that are not applicable.

Step 2 involves a number of assertions. If an error is reported, see in-line comments for potential problems.
"""

import os
import json
import scipy.io as sio
import wsrlib
from wsrdata.download_radar_scans import download_by_scan_list
from wsrdata.render_npy_arrays import render_by_scan_list

############### Step 1: define metadata ###############
DESCRIPTION         = "A mini roost dataset with bbox annotations for testing whether the " \
                      "data preparation pipeline is successfully set up. Three scans in the " \
                      "train and test splits respectively."
COMMENTS            = "(1) \"bbox\" is standardized to \"Dan Sheldon\" format using scaling factors " \
                      "learned by the EM algorithm proposed by Cheng et al. (2019), while " \
                      "the factors used are recorded in the \"bbox_scaling_factor\" field."
URL                 = ""
DATASET_VERSION     = "v0.1.0"
SPLIT_VERSION       = "v0.1.0"
ANNOTATION_VERSION  = "v1.0.0" # optional -- an empty string indicates a dataset without annotations
USER_MODEL_VERSION  = "v1.0.0_hardEM200000"
DATE_CREATED        = "2021/03/20"
LICENSES            = []
CATEGORIES          = ["roost"]

SPLIT_PATHS         = {"train": os.path.join("../static/splits", SPLIT_VERSION, "train.txt"),
                       "test": os.path.join("../static/splits", SPLIT_VERSION, "test.txt")}

ARRAY_VERSION       = "v0.1.0" # corresponding to arrays defined by the following lines
ARRAY_DIM           = 600
ARRAY_ATTRIBUTES    = ["reflectivity", "velocity", "spectrum_width"]
ARRAY_ELEVATIONS    = [0.5, 1.5, 2.5, 3.5, 4.5]
ARRAY_RENDER_CONFIG = {"fields":              ARRAY_ATTRIBUTES,
                       "coords":              "cartesian",
                       "r_min":               2125.0,     # default: first range bin of WSR-88D
                       "r_max":               150000.0,   # 459875.0 default: last range bin
                       "r_res":               250,        # default: super-res gate spacing
                       "az_res":              0.5,        # default: super-res azimuth resolution
                       "dim":                 ARRAY_DIM,  # num pixels on a side in Cartesian rendering
                       "sweeps":              None,
                       "elevs":               ARRAY_ELEVATIONS,
                       "use_ground_range":    True,
                       "interp_method":       'nearest'}
OVERWRITE_ARRAY     = False # whether to overwrite if npy arrays already exist

DUALPOL_VERSION         = "v0.1.0" # optional, corresponding to arrays defined by the following lines
DUALPOL_DIM             = 600
DUALPOL_ATTRIBUTES      = ["differential_reflectivity", "cross_correlation_ratio", "differential_phase"]
DUALPOL_ELEVATIONS      = [0.5, 1.5, 2.5, 3.5, 4.5]
DUALPOL_RENDER_CONFIG   = {"fields":              DUALPOL_ATTRIBUTES,
                           "coords":              "cartesian",
                           "r_min":               2125.0,       # default: first range bin of WSR-88D
                           "r_max":               150000.0,     # 459875.0 default: last range bin
                           "r_res":               250,          # default: super-res gate spacing
                           "az_res":              0.5,          # default: super-res azimuth resolution
                           "dim":                 DUALPOL_DIM,  # num pixels on a side in Cartesian rendering
                           "sweeps":              None,
                           "elevs":               DUALPOL_ELEVATIONS,
                           "use_ground_range":    True,
                           "interp_method":       "nearest"}
OVERWRITE_DUALPOL       = False # whether to overwrite if npy arrays already exist

# in most cases, no need to change the following
DATASET_DIR                 = f"../datasets/roosts-{DATASET_VERSION}"
ARRAY_CHANNELS              = [(attr, elev) for attr in ARRAY_ATTRIBUTES for elev in ARRAY_ELEVATIONS]
ARRAY_CHANNEL_INDICES       = {ARRAY_CHANNELS[i]: i for i in range(len(ARRAY_CHANNELS))}
ARRAY_SHAPE                 = (ARRAY_DIM, ARRAY_DIM, len(ARRAY_CHANNELS))
DUALPOL_CHANNELS            = [(attr, elev) for attr in DUALPOL_ATTRIBUTES for elev in DUALPOL_ELEVATIONS]
DUALPOL_CHANNEL_INDICES     = {DUALPOL_CHANNELS[i]: i for i in range(len(DUALPOL_CHANNELS))}
DUALPOL_SHAPE               = (DUALPOL_DIM, DUALPOL_DIM, len(DUALPOL_CHANNELS))
SCAN_ROOT_DIR               = "../static/scans"
SCAN_DIR                    = os.path.join(SCAN_ROOT_DIR, "scans")
SCAN_LOG_DIR                = os.path.join(SCAN_ROOT_DIR, "logs")
SCAN_LOG_NOT_S3_DIR         = os.path.join(SCAN_ROOT_DIR, "not_s3_logs")
SCAN_LOG_ERROR_SCANS_DIR    = os.path.join(SCAN_ROOT_DIR, "error_scan_logs")
ANNORATION_DIR              = os.path.join("../static/annotations", ANNOTATION_VERSION) if ANNOTATION_VERSION else ""
ARRAY_DIR                   = os.path.join("../static/arrays", ARRAY_VERSION)
DUALPOL_DIR                 = os.path.join("../static/arrays_for_dualpol", DUALPOL_VERSION) if DUALPOL_VERSION else ""


############### Step 2: check for conflicts, update logs, create directories ###############
# make sure DATASET_VERSION is not empty and does not conflict with existing versions, create a directory for it
assert DATASET_VERSION
if not os.path.exists(DATASET_DIR): os.mkdir(DATASET_DIR)
assert len(os.listdir(DATASET_DIR)) == 0
# make sure SPLIT_PATHS, SCAN_ROOT_DIR, etc exist
for split in SPLIT_PATHS: assert os.path.exists(SPLIT_PATHS[split])
if not os.path.exists(SCAN_ROOT_DIR): os.mkdir(SCAN_ROOT_DIR)
if not os.path.exists(SCAN_DIR): os.mkdir(SCAN_DIR)
if not os.path.exists(SCAN_LOG_DIR): os.mkdir(SCAN_LOG_DIR)
if not os.path.exists(SCAN_LOG_NOT_S3_DIR): os.mkdir(SCAN_LOG_NOT_S3_DIR)
if not os.path.exists(SCAN_LOG_ERROR_SCANS_DIR): os.mkdir(SCAN_LOG_ERROR_SCANS_DIR)
# make sure ANNOTATION_DIR exists when ANNOTATION_VERSION is not empty
if ANNOTATION_VERSION: assert os.path.exists(ANNORATION_DIR)

# make sure ARRAY_VERSION does not conflict with existing versions
assert os.path.exists("../static/arrays")
existing_versions = os.listdir("../static/arrays") # those currently in the directory
previous_versions = {} # those previously recorded at some point
if os.path.exists("../static/arrays/previous_versions.json"):
    with open("../static/arrays/previous_versions.json", "r") as f:
        previous_versions = json.load(f)
# make sure existing versions are all recorded in previous_versions.json
# if so, we use previous_versions.json as a reference to detect version conflicts
# otherwise, manual cleaning is required
for v in existing_versions:
    if v != "previous_versions.json":
        assert v in previous_versions
# make sure there is no conflict
# otherwise, either choose a new ARRAY_VERSION or clean the existing/previous version
if ARRAY_VERSION in previous_versions:
    assert previous_versions[ARRAY_VERSION] == ARRAY_RENDER_CONFIG
# initiate ARRAY_VERSION as a new version
else:
    previous_versions[ARRAY_VERSION] = ARRAY_RENDER_CONFIG
    with open("../static/arrays/previous_versions.json", "w") as f:
        json.dump(previous_versions, f)
    os.mkdir(ARRAY_DIR)

# check DUALPOL_VERSION similarly when it is not empty
if DUALPOL_VERSION:
    assert os.path.exists("../static/arrays_for_dualpol")
    existing_versions = os.listdir("../static/arrays_for_dualpol")  # those currently in the directory
    previous_versions = {}  # those previously recorded at some point
    if os.path.exists("../static/arrays_for_dualpol/previous_versions.json"):
        with open("../static/arrays_for_dualpol/previous_versions.json", "r") as f:
            previous_versions = json.load(f)
    # make sure existing versions are all recorded in previous_versions.json
    # if so, we use previous_versions.json as a reference to detect version conflicts
    # otherwise, manual cleaning is required
    for v in existing_versions:
        if v != "previous_versions.json":
            assert v in previous_versions
    # make sure there is no conflict
    # otherwise, either choose a new ARRAY_VERSION or clean the existing/previous version
    if DUALPOL_VERSION in previous_versions:
        assert previous_versions[DUALPOL_VERSION] == DUALPOL_RENDER_CONFIG
    # initiate DUALPOL_VERSION as a new version
    else:
        previous_versions[DUALPOL_VERSION] = DUALPOL_RENDER_CONFIG
        with open("../static/arrays_for_dualpol/previous_versions.json", "w") as f:
            json.dump(previous_versions, f)
        os.mkdir(DUALPOL_DIR)
else:
    DUALPOL_CHANNEL_INDICES = {}
    DUALPOL_SHAPE = ()
    DUALPOL_RENDER_CONFIG = {}


############### Step 3: sketch the dataset definition ###############
info = {
    "description":              DESCRIPTION,
    "comments":                 COMMENTS,
    "url":                      URL,
    "dataset_version":          DATASET_VERSION,
    "split_version":            SPLIT_VERSION,
    "annotation_version":       ANNOTATION_VERSION,
    "user_model_version":       USER_MODEL_VERSION,
    "date_created":             DATE_CREATED,
    "array_version":            ARRAY_VERSION,
    "array_channel_indices":    ARRAY_CHANNEL_INDICES,
    "array_shape":              ARRAY_SHAPE,
    "array_render_config":      ARRAY_RENDER_CONFIG,
    "dualpol_version":          DUALPOL_VERSION,
    "dualpol_channel_indices":  DUALPOL_CHANNEL_INDICES,
    "dualpol_shape":            DUALPOL_SHAPE,
    "dualpol_render_config":    DUALPOL_RENDER_CONFIG,
}

dataset = {
    "info":                 info,
    "license":              LICENSES,
    "arrays":               {split: [] for split in SPLIT_PATHS},
    "arrays_for_dualpol":   {split: [] for split in SPLIT_PATHS},
    "annotations":          {split: [] for split in SPLIT_PATHS},
    "categories":           CATEGORIES,
}


############### Step 4: Download radar scans by splits ###############
print("Downloading scans...")
for split in SPLIT_PATHS:
    download_by_scan_list(
        SPLIT_PATHS[split], SCAN_DIR,
        os.path.join(SCAN_LOG_DIR, f"{DATASET_VERSION}.log"),
        os.path.join(SCAN_LOG_NOT_S3_DIR, f"{DATASET_VERSION}.log"),
        os.path.join(SCAN_LOG_ERROR_SCANS_DIR, f"{DATASET_VERSION}.log")
    )


############### Step 5: Render radar scans by splits ###############
print("Rendering arrays...")
for split in SPLIT_PATHS:
    render_by_scan_list(
        SPLIT_PATHS[split], SCAN_DIR,
        ARRAY_RENDER_CONFIG, ARRAY_ATTRIBUTES, ARRAY_DIR, OVERWRITE_ARRAY,
        DUALPOL_RENDER_CONFIG, DUALPOL_ATTRIBUTES, DUALPOL_DIR, OVERWRITE_DUALPOL,
    )

############### Step 6: Populate the dataset definition and save to json ###############
print("Populating the dataset definition...")
for split in SPLIT_PATHS:
    scans = [scan.strip() for scan in open(SPLIT_PATHS[split], "r").readlines()]
    id = 0 # for arrays and dualpol arrays
    annotation_id = 0

    for scan in scans:
        # add array to dataset
        dataset["arrays"][split].append({
            "id": id,
            "path": os.path.join(ARRAY_DIR, scan+".npy"),
            "scan": scan,
        })

        # add dualpol array to dataset
        if DUALPOL_VERSION:
            dataset["arrays_for_dualpol"][split].append({
                "id": id,
                "path": os.path.join(DUALPOL_DIR, scan+"_dualpol.npy"),
                "scan": scan,
            })

        id += 1

        # add annotations to dataset
        if ANNOTATION_VERSION:
            annotation_path = os.path.join(ANNORATION_DIR, scan + ".mat")
            boxes = sio.loadmat(annotation_path, struct_as_record=False, squeeze_me=True)['label'].boxes
            boxes = boxes - 1 # python and matlab use 0 and 1-based indexing respectively
            if boxes.ndim == 1: boxes = boxes[np.newaxis, :]
            for box in boxes:
                dataset["anntations"][split].append({
                    "id": int,
                    "array_id": int,
                    "category_id": int,
                    "bbox": [x, y, width, height],
                    "bbox_annotator": str,
                    "bbox_scaling_factor": 1.0,
                })
                annotation_id += 1


print("Saving the dataset definition to json...")
with open(f"../datasets/roosts-{DATASET_VERSION}/roosts-{DATASET_VERSION}.json", 'w') as f:
    json.dump(dataset, f)

print("All done.")