# Here we consider a csv with the following columns:

DATASET_JSON_PATH = "../datasets/roosts-v0.1.0-official/"
CSV_FIELDS = ["track_id", "filename", "from_sunrise", "det_score", "x", "y", "r", "lon", "lat", "radius"]

with open(DATASET_JSON_PATH, "r") as f:
    dataset = json.load(f)

