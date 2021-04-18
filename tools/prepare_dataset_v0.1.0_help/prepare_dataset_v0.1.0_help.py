"""
Help script for rendering using several processes
"""

import os
import json
import numpy as np
import scipy.io as sio
import wsrlib
from wsrdata.download_radar_scans import download_by_scan_list
from wsrdata.render_npy_arrays import render_by_scan_list

############### Step 1: define metadata ###############
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
CATEGORIES          = ["roost"]
DEFAULT_CAT_ID      = 0 # by default, annotations are for CATEGORIES[0] which is "roost" in this template
OVERWRITE_DATASET   = True # overwrites the previous json file if the specified dataset version already exists

SPLIT_PATHS         = {"part": os.path.join("../static/splits", SPLIT_VERSION, "test_2.txt")}

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
OVERWRITE_ARRAY     = False # whether to overwrite if npy arrays already exist

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
OVERWRITE_DUALPOL       = False # whether to overwrite if npy arrays already exist

# in most cases, no need to change the following
SCAN_ROOT_DIR               = "../static/scans"
SCAN_DIR                    = os.path.join(SCAN_ROOT_DIR, "scans")
SCAN_LOG_DIR                = os.path.join(SCAN_ROOT_DIR, "logs")
SCAN_LOG_NOT_S3_DIR         = os.path.join(SCAN_ROOT_DIR, "not_s3_logs")
SCAN_LOG_ERROR_SCANS_DIR    = os.path.join(SCAN_ROOT_DIR, "error_scan_logs")
ARRAY_CHANNELS              = [f"{attr}-{elev}" for attr in ARRAY_ATTRIBUTES for elev in ARRAY_ELEVATIONS]
ARRAY_CHANNEL_INDICES       = {ARRAY_CHANNELS[i]: i for i in range(len(ARRAY_CHANNELS))}
ARRAY_SHAPE                 = (len(ARRAY_CHANNELS), ARRAY_DIM, ARRAY_DIM)
ARRAY_DIR                   = os.path.join("../static/arrays", ARRAY_VERSION)
DUALPOL_CHANNELS            = [f"{attr}-{elev}" for attr in DUALPOL_ATTRIBUTES for elev in DUALPOL_ELEVATIONS]
DUALPOL_CHANNEL_INDICES     = {DUALPOL_CHANNELS[i]: i for i in range(len(DUALPOL_CHANNELS))}
DUALPOL_SHAPE               = (len(DUALPOL_CHANNELS), DUALPOL_DIM, DUALPOL_DIM)
DUALPOL_DIR                 = os.path.join("../static/arrays_for_dualpol", DUALPOL_VERSION)
ANNOTATION_DIR              = os.path.join("../static/annotations", ANNOTATION_VERSION) if ANNOTATION_VERSION else ""
BBOX_MODE                   = "XYWH"
DATASET_DIR                 = f"../datasets/roosts-{DATASET_VERSION}"


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
        ARRAY_RENDER_CONFIG, ARRAY_ATTRIBUTES, ARRAY_DIR,
        DUALPOL_RENDER_CONFIG, DUALPOL_ATTRIBUTES, DUALPOL_DIR,
    )

