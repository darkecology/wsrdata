This directory contains helper functions that can be useful for accelerating the creation of 
dataset v0.1.0 and checking the correctness of the creation.

Since the dataset is pretty large, we split `static/splits/v0.1.0/v0.1.0_ordered_splits/{train,test}.txt` 
into `train_*.txt` and `test_*.txt` under this directory.
`static/splits/v0.1.0/v0.1.0_ordered_splits/val.txt` is not split since it's comparatively small.

For record, we copied the generated 
`static/arrays/v0.1.0/{rendering.log, array_error_scans.log, dualpol_error_scans.log}` to this directory.

Typically `previous_versions.json` under `static/arrays` will be updated to avoid future version conflicts.
When it is not done by `prepare_dataset_*.py`, use `log_array_version.py` to manually update them.

`error_check.py` collects unexpected errors from `rendering.log` and write to `rendering_exceptions.txt`.