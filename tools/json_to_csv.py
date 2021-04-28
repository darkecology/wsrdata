import json

DATASET_JSON_PATH = "../datasets/roosts_v1.0.0.json"
CSV_FIELDS = ["track_id", "filename", "from_sunrise", "det_score", "x", "y", "r", "lon", "lat", "radius"]

with open(DATASET_JSON_PATH, "r") as f:
    dataset = json.load(f)
