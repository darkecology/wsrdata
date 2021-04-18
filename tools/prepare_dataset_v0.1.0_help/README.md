This directory contains helper functions that can be useful for accelerating the creation of 
dataset v0.1.0 and checking the correctness of the creation.

Since the dataset is pretty large, we split `static/splits/v0.1.0/v0.1.0-standard/{train,test}.txt` 
into `train_*.txt` and `test_*.txt` under this directory.
`static/splits/v0.1.0/v0.1.0-standard/val.txt` is not split since it's comparatively small.
Modify and launch `prepare_dataset_v0.1.0_help.py` for each subset for parallel downloading and rendering.

For record, we copied the generated `static/arrays/v0.1.0/rendering.log`
to this directory; `static/arrays/v0.1.0/errors.log` and `static/arrays_for_dualpol/v0.1.0/errors.log`
to `array_error_scans.log` and `dualpol_error_scans.log` under this directory.

Typically `previous_versions.json` under `static/arrays` will be updated to avoid future version conflicts.
When it is not done by `prepare_dataset_*.py`, use `log_array_version.py` to manually update them.

`prepare_dataset_v0.1.0_error_check.py` collects unexpected errors from `rendering.log`
and write to `rendering_exceptions.txt`.