import json

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

with open("../static/arrays/previous_versions.json", "r") as f:
    previous_versions = json.load(f)

previous_versions[ARRAY_VERSION] = ARRAY_RENDER_CONFIG
with open("../static/arrays/previous_versions.json", "w") as f:
    json.dump(previous_versions, f, indent=4)


with open("../static/arrays_for_dualpol/previous_versions.json", "r") as f:
    previous_versions = json.load(f)

previous_versions[DUALPOL_VERSION] = DUALPOL_RENDER_CONFIG
with open("../static/arrays_for_dualpol/previous_versions.json", "w") as f:
    json.dump(previous_versions, f, indent=4)