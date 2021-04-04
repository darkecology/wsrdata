This directory contains helper functions that can be useful for accelerating the creation of 
dataset v1.0.0 and checking the correctness of the creation process.

Since the dataset is pretty large, we split **static/splits/v1.0.0/train.txt** and 
**static/splits/v1.0.0/test.txt** into **train_\*.txt** and **test_\*.txt** in this directory.
**static/splits/v1.0.0/val.txt** is not split since it's comparatively small.
Modify and launch **prepare_dataset_v1.0.0_help.py** for the subsets respectively for parallel 
downloading and rendering.

For record, we copied the generated **static/arrays/v1.0.0/rendering.log**
to this directory; **static/arrays/v1.0.0/errors.log** and **static/arrays_for_dualpol/v1.0.0/errors.log**
to **array_error_scans.log** and **dualpol_error_scans.log**.

Typically **previous_versions.json** under **static/arrays** and **static/arrays_for_dualpol**
will both be updated to avoid future version conflicts.
If not done by **prepare_dataset_\*.py**, use **log_array_version.py** to manually update them.

Use **prepare_dataset_v1.0.0_error_check.py** to collect unexpected errors from **rendering.log**
and write to **rendering_exceptions.txt**.