"""
This script runs the data preparation pipeline to create the toy dataset v0.1.0.
It can be modified to create customized datasets.

In most cases, changing values for VARIABLEs in Step 1 suffices.
Use None, empty lists, empty strings, etc to fill fields that are not applicable.

Step 2 involves a number of assertions. If an error is reported, see in-line comments for potential problems.
Common reasons for assertion errors and solutions include:
(1) OVERWRITE_DATASET=FALSE but the dataset version already exists
Solution: change DATASET_VERSION or delete the previous version under ../datasets.
(2) ARRAY_RENDER_CONFIG and DUALPOL_RENDER_CONFIG conflicts with previous configs of same ARRAY/DUALPOL_VERSION
Solution: change ARRAY_VERSION/DUALPOL_VERSION or clean ../static/arrays and ../static/arrays_for_dualpol,
including previous_version.json under both directories.

If there is a standard annotation format in the future,
annotation-related code (including those in Step 6) will need to be modified accordingly.
"""

import os
import json
import numpy as np
import scipy.io as sio
import wsrlib
from wsrdata.download_radar_scans import download_by_scan_list
from wsrdata.render_npy_arrays import render_by_scan_list

############### Step 1: define metadata ###############
PRETTY_PRINT_INDENT = None # default None; if integer n, generated json will be human-readable with n indentations

DESCRIPTION         = "The official wsrdata roost dataset v1.0.0 with bbox annotations."
COMMENTS            = "(1) \"bbox\" is standardized to \"Dan Sheldon\" format using scaling factors " \
                      "learned by the EM algorithm proposed by Cheng et al. (2019), while " \
                      "the factors used are recorded in the \"bbox_scaling_factor\" field." #TODO
URL                 = ""
DATASET_VERSION     = "v1.0.0"
SPLIT_VERSION       = "v1.0.0"
ANNOTATION_VERSION  = "v1.0.0" # optional -- an empty string indicates a dataset without annotations
USER_MODEL_VERSION  = "v1.0.0_hardEM200000"
DATE_CREATED        = "2021/03/20"
LICENSES            = [{"url": "http://www.apache.org/licenses/",
                        "id": 0, "name": "Apache License 2.0"},
                       {"url": "http://creativecommons.org/licenses/by-nc-sa/2.0/",
                        "id": 1, "name": "Attribution-NonCommercial-ShareAlike License"},
                       {"url": "http://creativecommons.org/licenses/by-nc/2.0/",
                        "id": 2, "name": "Attribution-NonCommercial License"},
                       {"url": "http://creativecommons.org/licenses/by-nc-nd/2.0/",
                        "id": 3, "name": "Attribution-NonCommercial-NoDerivs License"},
                       {"url": "http://creativecommons.org/licenses/by/2.0/",
                        "id": 4, "name": "Attribution License"},
                       {"url": "http://creativecommons.org/licenses/by-sa/2.0/",
                        "id": 5, "name": "Attribution-ShareAlike License"},
                       {"url": "http://creativecommons.org/licenses/by-nd/2.0/",
                        "id": 6, "name": "Attribution-NoDerivs License"},
                       {"url": "http://flickr.com/commons/usage/",
                        "id": 7, "name": "No known copyright restrictions"},
                       {"url": "http://www.usa.gov/copyright.shtml",
                        "id": 8, "name": "United States Government Work"}]
                        # the above 0 is a common license used by many large open-source projects including Detectron2
                        # the above 1-8 are licenses from the COCO dataset
DEFAULT_LIC_ID      = 0 # by default, use LICENSES[0] for the rendered arrays
CATEGORIES          = ["roost"]
DEFAULT_CAT_ID      = 0 # by default, annotations are for CATEGORIES[0] which is "roost" in this template
OVERWRITE_DATASET   = True # overwrites the previous json file if the specified dataset version already exists

SPLIT_PATHS         = {"train": os.path.join("../static/splits", SPLIT_VERSION, "train.txt"),
                       "val": os.path.join("../static/splits", SPLIT_VERSION, "val.txt"),
                       "test": os.path.join("../static/splits", SPLIT_VERSION, "test.txt")}

ARRAY_VERSION       = "v1.0.0" # corresponding to arrays defined by the following lines
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

DUALPOL_VERSION         = "v1.0.0" # corresponding to arrays defined by the following lines
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

# manually imported from static/user_models/v1.0.0/hardEM200000_user_model_python2.pkl
BBOX_SCALING_FACTORS    = {'Ftian-KOKX': 0.7827008296465084,
                           'William Curran-KDOX': 0.6671858060703622,
                           'andrew-KAMX': 0.8238429277541144,
                           'andrew-KHGX': 0.8021155634196264,
                           'andrew-KJAX': 0.9397206576582352,
                           'andrew-KLCH': 0.7981654079788019,
                           'andrew-KLIX': 1.003359702917803,
                           'andrew-KMLB': 0.8846939182400024,
                           'andrew-KTBW': 1.0745160463520484,
                           'andrew-KTLH': 0.8121429842343971,
                           'anon-KDOX': 0.6393409410259764,
                           'anon-KLIX': 0.8789372720576193,
                           'anon-KTBW': 0.8777182885471609,
                           'jafer1-KDOX': 0.643700604491143,
                           'jafermjj-KDOX': 0.629814055371781,
                           'jberger1-KAMX': 1.0116521039423771,
                           'jberger1-KLIX': 0.9350564477085113,
                           'jberger1-KMLB': 1.01208151592683,
                           'jberger1-KTBW': 1.0710975633513655,
                           'jpodrat-KLIX': 1.0258838999961304,
                           'sheldon-KAMX': 1.0190194757755286,
                           'sheldon-KDOX': 0.6469252517936639,
                           'sheldon-KLIX': 0.7086575697533594,
                           'sheldon-KMLB': 0.8441916918113227,
                           'sheldon-KOKX': 0.6049163038774339,
                           'sheldon-KRTX': 0.5936236006148872,
                           'sheldon-KTBW': 0.7830289430054851,}

# in most cases, no need to change the following
SCAN_ROOT_DIR               = "../static/scans"
SCAN_DIR                    = os.path.join(SCAN_ROOT_DIR, "scans")
SCAN_LOG_DIR                = os.path.join(SCAN_ROOT_DIR, "logs")
SCAN_LOG_NOT_S3_DIR         = os.path.join(SCAN_ROOT_DIR, "not_s3_logs")
SCAN_LOG_ERROR_SCANS_DIR    = os.path.join(SCAN_ROOT_DIR, "error_scan_logs")
ARRAY_CHANNELS              = [(attr, elev) for attr in ARRAY_ATTRIBUTES for elev in ARRAY_ELEVATIONS]
ARRAY_CHANNEL_INDICES       = {attr:{} for attr in ARRAY_ATTRIBUTES}
for i, (attr, elev) in enumerate(ARRAY_CHANNELS):
    ARRAY_CHANNEL_INDICES[attr][elev] = i # elev will become str when saved to json
ARRAY_SHAPE                 = (len(ARRAY_CHANNELS), ARRAY_DIM, ARRAY_DIM)
ARRAY_DIR                   = os.path.join(os.getcwd(), "../static/arrays", ARRAY_VERSION)
DUALPOL_CHANNELS            = [(attr, elev) for attr in DUALPOL_ATTRIBUTES for elev in DUALPOL_ELEVATIONS]
DUALPOL_CHANNEL_INDICES     = {attr:{} for attr in DUALPOL_ATTRIBUTES}
for i, (attr, elev) in enumerate(DUALPOL_CHANNELS):
    DUALPOL_CHANNEL_INDICES[attr][elev] = i
DUALPOL_SHAPE               = (len(DUALPOL_CHANNELS), DUALPOL_DIM, DUALPOL_DIM)
DUALPOL_DIR                 = os.path.join(os.getcwd(), "../static/arrays_for_dualpol", DUALPOL_VERSION)
ANNOTATION_DIR              = os.path.join("../static/annotations", ANNOTATION_VERSION) if ANNOTATION_VERSION else ""
BBOX_MODE                   = "XYWH"
DATASET_DIR                 = f"../datasets/roosts-{DATASET_VERSION}"


############### Step 2: check for conflicts, update logs, create directories ###############
# make sure DATASET_VERSION is not empty and does not conflict with existing versions, create a directory for it
assert DATASET_VERSION
if not os.path.exists(DATASET_DIR): os.mkdir(DATASET_DIR)
if not OVERWRITE_DATASET: assert len(os.listdir(DATASET_DIR)) == 0
# make sure SPLIT_PATHS, SCAN_ROOT_DIR, etc exist
for split in SPLIT_PATHS: assert os.path.exists(SPLIT_PATHS[split])
if not os.path.exists(SCAN_ROOT_DIR): os.mkdir(SCAN_ROOT_DIR)
if not os.path.exists(SCAN_DIR): os.mkdir(SCAN_DIR)
if not os.path.exists(SCAN_LOG_DIR): os.mkdir(SCAN_LOG_DIR)
if not os.path.exists(SCAN_LOG_NOT_S3_DIR): os.mkdir(SCAN_LOG_NOT_S3_DIR)
if not os.path.exists(SCAN_LOG_ERROR_SCANS_DIR): os.mkdir(SCAN_LOG_ERROR_SCANS_DIR)
# make sure ANNOTATION_DIR exists when ANNOTATION_VERSION is not empty
if ANNOTATION_VERSION: assert os.path.exists(ANNOTATION_DIR)

# make sure ARRAY_VERSION is not empty and does not conflict with existing versions
assert ARRAY_VERSION
if not os.path.exists("../static/arrays"): os.mkdir("../static/arrays")
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
# make sure there is no config conflict
# otherwise, either choose a new ARRAY_VERSION or clean the existing/previous version
if ARRAY_VERSION in previous_versions:
    assert previous_versions[ARRAY_VERSION] == ARRAY_RENDER_CONFIG
# initiate ARRAY_VERSION as a new version
else:
    previous_versions[ARRAY_VERSION] = ARRAY_RENDER_CONFIG
    with open("../static/arrays/previous_versions.json", "w") as f:
        json.dump(previous_versions, f, indent=PRETTY_PRINT_INDENT)
if not os.path.exists(ARRAY_DIR): os.mkdir(ARRAY_DIR)

# make sure DUALPOL_VERSION is not empty and does not conflict with existing versions
assert DUALPOL_VERSION
if not os.path.exists("../static/arrays_for_dualpol"): os.mkdir("../static/arrays_for_dualpol")
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
# make sure there is no config conflict
# otherwise, either choose a new ARRAY_VERSION or clean the existing/previous version
if DUALPOL_VERSION in previous_versions:
    assert previous_versions[DUALPOL_VERSION] == DUALPOL_RENDER_CONFIG
# initiate DUALPOL_VERSION as a new version
else:
    previous_versions[DUALPOL_VERSION] = DUALPOL_RENDER_CONFIG
    with open("../static/arrays_for_dualpol/previous_versions.json", "w") as f:
        json.dump(previous_versions, f, indent=PRETTY_PRINT_INDENT)
if not os.path.exists(DUALPOL_DIR): os.mkdir(DUALPOL_DIR)


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
    "categories":               CATEGORIES,
    "bbox_mode":                BBOX_MODE,
    "bbox_scaling_factors":     BBOX_SCALING_FACTORS,
}

dataset = {
    "info":                 info,
    "license":              LICENSES,
    "scans":                {split: [] for split in SPLIT_PATHS},
}


############### Step 4: Download radar scans by splits ###############
print("Downloading scans...")
download_errors = {}
for split in SPLIT_PATHS:
    download_errors[split] = download_by_scan_list(
        SPLIT_PATHS[split], SCAN_DIR,
        os.path.join(SCAN_LOG_DIR, f"{DATASET_VERSION}.log"),
        os.path.join(SCAN_LOG_NOT_S3_DIR, f"{DATASET_VERSION}.log"),
        os.path.join(SCAN_LOG_ERROR_SCANS_DIR, f"{DATASET_VERSION}.log")
    )


############### Step 5: Render radar scans by splits ###############
print("Rendering arrays...")
array_errors = {}
dualpol_errors = {}
for split in SPLIT_PATHS:
    array_errors[split], dualpol_errors[split] = render_by_scan_list(
        SPLIT_PATHS[split], SCAN_DIR,
        ARRAY_RENDER_CONFIG, ARRAY_ATTRIBUTES, ARRAY_DIR,
        DUALPOL_RENDER_CONFIG, DUALPOL_ATTRIBUTES, DUALPOL_DIR,
    )


############### Step 6: Populate the dataset definition and save to json ###############
print("Populating the dataset definition...")
for split in SPLIT_PATHS:
    print(f"Starting the {split} split...")
    scans = [scan.strip() for scan in open(SPLIT_PATHS[split], "r").readlines()]
    scan_id = 0 # for arrays and dualpol arrays

    if ANNOTATION_VERSION:
        print("Loading annotations....")
        annotation_id = 0

        # annotations ordered alphabetically by scan, then by date, then by track, but not by second
        # fields are: 0 scan_id (different than ours), 1 filename, 2 sequence_id, 3 station, 4 year, 5 month,
        #         6 day, 7 hour, 8 minute, 9 second, 10 minutes_from_sunrise, 11 x, 12 y, 13 r, 14 username
        annotations = [annotation.strip().split(",") for annotation in
                       open(os.path.join(ANNOTATION_DIR, "user_annotations.txt"), "r").readlines()[1:]]
        # Preparation: load annotations into a dictionary where scan names are keys
        annotation_dict = {}
        minutes_from_sunrise_dict = {}
        unknown_scaling_factors = set()
        for annotation in annotations:
            annotation[11] = float(annotation[11])
            annotation[12] = float(annotation[12])
            annotation[13] = float(annotation[13])
            # if annotation[14] in BBOX_SCALING_FACTORS:
            #     factor = BBOX_SCALING_FACTORS[annotation[14]]
            # else:
            #     unknown_scaling_factors.add(annotation[14])
            #     factor = None
            x_im = (annotation[11] + ARRAY_RENDER_CONFIG["r_max"]) * ARRAY_DIM / (2 * ARRAY_RENDER_CONFIG["r_max"])
            y_im = (annotation[12] + ARRAY_RENDER_CONFIG["r_max"]) * ARRAY_DIM / (2 * ARRAY_RENDER_CONFIG["r_max"])
            r_im = annotation[13] * ARRAY_DIM / (2 * ARRAY_RENDER_CONFIG["r_max"])
            new_annotation = {
                "sequence_id": int(annotation[2]),
                "category_id": DEFAULT_CAT_ID,
                "x": annotation[11],
                "y": annotation[12],
                "r": annotation[13],
                "x_im": x_im,
                "y_im": y_im,
                "r_im": r_im,
                "bbox": [int(x_im-r_im), int(y_im-r_im),
                         int(x_im+r_im)-int(x_im-r_im)+1, int(y_im+r_im)-int(y_im-r_im)+1],
                "bbox_annotator": annotation[14],
                # "bbox_scaling_factor": factor,
            }
            if annotation[1][:-3] in annotation_dict:
                annotation_dict[annotation[1][:-3]].append(new_annotation)
            else:
                annotation_dict[annotation[1][:-3]] = [new_annotation]
            minutes_from_sunrise_dict[annotation[1][:-3]] = int(annotation[10])
        print(f"Unknown user models / bbox scaling factors for {unknown_scaling_factors} but "
              f"fine as long as the train/val/test split does not include these user-station pairs.")

    for n, scan in enumerate(scans):
        # add array to dataset
        dataset["scans"][split].append({
            "scan_id":              scan_id,
            "scan":                 scan,
            "minutes_from_sunrise": minutes_from_sunrise_dict[scan] if scan in minutes_from_sunrise_dict else None,
            "array_path":           os.path.join(ARRAY_DIR, scan+".npy"),
            "array_license_id":     DEFAULT_LIC_ID,
            "dualpol_path":         os.path.join(DUALPOL_DIR, scan+"_dualpol.npy"),
            "dualpol_license_id":   DEFAULT_LIC_ID,
            "annotations":          annotation_dict[scan] if ANNOTATION_VERSION and scan in annotation_dict else [],
        })

        for annotation in dataset["scans"][split][-1]["annotations"]:
            annotation["annotation_id"] = annotation_id
            annotation_id += 1
            annotation["scan_id"] = scan_id

            if annotation["bbox_annotator"] in unknown_scaling_factors:
                print(f"Problem: annotation {annotation_id} for scan {scan_id} involves unknown "
                      f"annotator-station pair and scaling factor.")

        scan_id += 1


print("Saving the dataset definition to json...")
with open(f"../datasets/roosts-{DATASET_VERSION}/roosts-{DATASET_VERSION}.json", 'w') as f:
    json.dump(dataset, f, indent=PRETTY_PRINT_INDENT)

print("All done.")