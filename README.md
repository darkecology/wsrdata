# wsrdata
Weather surveillance radar archives hold detailed information about biological phenomena in the atmosphere.
Given radar scans and specifications, this repository prepares datasets for training and evaluating 
machine learning models for detecting and tracking communal bird roosts. 

### Under Construction
- Which user models (i.e. scaling factors) to use for bbox annotations? 
Conversion between json and csv and use web interface to check

### Overview
- **datasets** is a directory reserved for json files created by this repository 
to define datasets in the modified [COCO format](https://cocodataset.org/#format-data) demonstrated below.
We use 0-based indexing for all ids; None, empty lists, empty strings, etc to indicate "not applicable".
    ```angular2
    {
        "info":                   info,
        "license":                [license],
        "scans":                  {"train": [scan], "val": [scan], "test": [scan]},
    }
  
    info = {
        "description":              "A roost dataset with annotations.",
        "comments":                 "Design choices and technical details can be commented here.",
        "url":                      "",
        "dataset_version":          "v0.0.1",
        "split_version":            "v0.0.1",
        "annotation_version":       "v0.0.1",
        "user_model_version":       "v0.0.1_hardEM200000",
        "date_created":             "yyyy/mm/dd",
        "array_version":            "v0.0.1",
        "array_channel_indices":    {"reflectivity":      {0.5: 0,
                                                           1.5: 1,
                                                           ...},
                                     "velocity":          {0.5: 5,
                                                           1.5: 6,
                                                           ...},
                                     "spectrum_width":    {0.5: 10,
                                                           1.5: 11,
                                                           ...}},
        "array_shape":              (15, 600, 600),
        "array_render_config":      render_config,
        "dualpol_version":          "v0.0.1",
        "dualpol_channel_indices":  {"differential_reflectivity":   {"0.5": 0,
                                                                     "1.5": 1,
                                                                     ...},
                                     "cross_correlation_ratio":     {"0.5": 5,
                                                                     "1.5": 6,
                                                                     ...},
                                     "differential_phase":          {"0.5": 10,
                                                                     "1.5": 11,
                                                                     ...}},
        "dualpol_shape":            (15, 600, 600),
        "dualpol_render_config":    render_config,
        "categories":               ["roost", "rain", ...],
        "bbox_mode":                "XYWH",
        "bbox_scaling_factors":     {..., "sheldon-KDOX": 0.6469252517936639, ...}
    }
  
    render_config = {
        "fields":            ["reflectivity", "velocity", ...],
        "coords":            "polar"/"cartesian",
        "r_min":             2125.0,     # default: first range bin of WSR-88D
        "r_max":             150000.0,   # default: 459875.0, last range bin
        "r_res":             250,        # default: super-res gate spacing
        "az_res":            0.5,        # default: super-res azimuth resolution
        "dim":               600,        # num pixels on a side in Cartesian rendering
        "sweeps":            None,
        "elevs":             [0.1, 1.5, 2.5, 3.5, 4.5],
        "use_ground_range":  True,
        "interp_method":     "nearest"
    }
  
    license = {
        "id":     int,
        "name":   str,
        "url":    str,
    }
  
    scan = {
        "scan_id":                int,
        "scan":                   str,    # scan name
        "minutes_from_sunrise":   int,    # None for unknown, negative for before sunrise
        "array_path":             str,
        "array_license_id":       int,
        "dualpol_path":           str,
        "dualpol_license_id":     int,
        "annotations":            [annotation],
    }
    
    annotation = {
        "annotation_id":          int,    # among all annotations of all scans
        "scan_id":                int,
        "sequence_id":            int,    # indices for roost tracks
        "category_id":            int,
        "x":                      float,  # circle center coordinate in map
        "y":                      float,
        "r":                      float,  # circle radius
        "x_im":                   float,  # circle center coordinate in array
        "y_im":                   float,
        "r_im":                   float,  # circle radius normalized to array dim
        "bbox":                   [x, y, width, height],  # calculated from x_im y_im r_im
        "bbox_annotator":         str,
        "bbox_scaling_factor":    float,  # bbox_scaling_factors[bbox_annotator] or None
        "segmentation":           [polygon],
        "segmentation_annotator": str,
    }
    ```

- **datasets/roosts-v0.1.0-official** defines a toy dataset as a reference:
    - **roosts-v0.1.0.json** is a human-readable json generated with line indentation of 4
    - **visualization** contains scan visualization (with bounding boxes) which can be generated using 
    **tools/visualization.py** and **tools/visualization.ipynb**

- **src/wsrdata** implements functions relevant to dataset preparation and analyses:
    - **download_radar_scans.py** downloads radar scans
    - **render_npy_arrays.py** renders npy arrays from radar scans
    - **utils** contains utility/help functions

- **static** contains static files that are inputs to the dataset preparation pipeline or 
generated during the preparation (see the following Release section more info):
    - **splits** is for different versions of data splits
    - **scans** is reserved for downloaded radar scans
    - **annotations** is for different versions of annotations
        - Note: For dataset v0.1.0, a csv file named **user_annotations.txt** is used as the source of annotations. 
        If in the future there is a new input format for annotations, related code including that in 
        step 6 of **tools/prepare_dataset_\*.py** will need to be updated.
    - **user_models** is for different versions of bounding box scaling factors learned by EM [1]
    - **arrays** is for different versions of npy arrays rendered from scans according to splits
    - **arrays_for_dualpol** is for different versions of dualpol npy arrays rendered from scans according to splits

- **tools** contains scripts that are entry points of the data preparation pipeline,
 call functions in **src/wsrdata**, and partially or entirely run the dataset preparation pipeline:
    - **prepare_dataset_v0.1.0.py** is a modifiable template that, given metadata,
    download radar scans, render npy arrays, read annotations, and create json files which define datasets
    - **visualization.py** generates npg images that visualize channels in npy arrays for a list of scans 
    with annotations from a json file
    - **visualization.ipynb** can interactively (1) render and visualize a scan and 
    (2) visualize channels from a npy array with its annotation(s) from a json file

### Release
#### datasets
- **roosts-v0.1.0-official** uses splits v0.1.0, annotations v1.0.0, user_models v1.0.0_hardEM200000,
 arrays v0.1.0, arrays_for_dualpol v0.1.0.
    - **roosts-v0.1.0-official.json** defines the dataset
- **roosts-v1.0.0-official** uses splits v1.0.0, annotations v1.0.0, user_models v1.0.0_hardEM200000,
 arrays v1.0.0, arrays_for_dualpol v1.0.0.

#### splits
- **v0.1.0** involves 3 scans in train.txt and test.txt respectively and 
can be used to test whether the dataset preparation pipeline is successfully set up.
- **v0.5.0** is the split used in [1] and involves 88972 scans. Scans are randomly split by day-station, 
i.e. scans from the same day at the same station are all in one of train.txt, val.txt, and test.txt.
Scans are randomly ordered in the txt files.
    - **train.txt**: 53600 scans, among which 26895 are in annotation v1.0.0, ~60.24%
    - **val.txt**: 11658 scans, among which 3796 are in annotation v1.0.0, ~13.10%
    - **test.txt**: 23714 scans, among which 7711 are in annotation v1.0.0, ~26.65%
- **v1.0.0** contains the same scans as v0.5.0, with scans ordered in the txt files.

#### annotations
- Annotation information is collected from a few sources in various formats. It would be nice to establish
a standard format in the future and standard code in Step 6 of `tools/prepare_dataset_*.py` to load annotations.
- **v1.0.0** is reserved for annotation sources and includes processing scripts. This annotation version 
is listed in the txt file [here](https://www.dropbox.com/s/0j9srf0jt6lc76e/user_annotations.txt?dl=0); 
annotation information in the txt file were processed and paritially saved in *.mat files 
[here](https://www.dropbox.com/s/eti469m1z4634x4/Annotations.zip?dl=0) and used by [1]; 
annotator information was also logged 
[here](https://docs.google.com/spreadsheets/d/1lvEWNSSJsT9WYGgUE3rIkOoy9vU2zHEPTCiVJnRdFaI/edit).

#### user_models
- **v1.0.0** can be found [here](https://www.dropbox.com/sh/d3ronsvzr9c0xxq/AAD9fgrk2exRuyWcBjtU7Ea8a?dl=0),
where the pkl files can be loaded by python 2 but not python 3. User models are bounding box scaling factors learned
by EM. Consider outputs of Faster RCNN in [1] as ground truth: User factor = biased user annotation / ground truth.
User factors are currently manually imported to `tools/prepare_dataset_v0.1.0.py`.

#### arrays
- **v0.1.0**: 600x600x15 arrays where the channels are _[reflectivity, velocity, spectrum_width] x 
elevations [0.5, 1.5, 2.5, 3.5, 4.5]_.
- **v1.0.0**: same attributes as v0.1.0.

#### arrays_for_dualpol
- **v0.1.0**: 600x600x15 arrays where the channels are _[differential_reflectivity, cross_correlation_ratio, differential_phase] x 
elevations [0.5, 1.5, 2.5, 3.5, 4.5]_.
- **v1.0.0**: same attributes as v0.1.0.

### Installation
Create and activate a python 3.6 environment. Check the cuda version at, for example, `/usr/local/cuda`, 
or potentially by `nvcc -V`. We use cuda 10.1. 
Install a compatible version of [PyTorch](https://pytorch.org/get-started/previous-versions/).
```bash
conda create -n roost2021 python=3.6
conda activate roost2021
pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
```

Assume we are under a roost project directory `roosts2021`. Let's create a `libs` directory where
we will install the pywsrlib toolkit and data preparation functions in this repository. 
```bash
mkdir libs
cd libs

pip install netCDF4==1.5.6 scipy==1.5.4 matplotlib==3.3.4 pandas==1.1.5 more-itertools==8.7.0
git clone https://github.com/darkecology/pywsrlib
cd pywsrlib
pip install -e .
cd ..

git clone https://github.com/darkecology/wsrdata.git
cd wsrdata
pip install -e .
```

[Configure AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) 
in order to download radar scans. 
Enter `AWS Access Key ID` and `AWS Secret Access Key` as prompted,
`us-east-1` for `Default region name`, and nothing for `Default output format`.
```bash
aws configure
```
Review the updated AWS config.
```bash
vim ~/.aws/credentials
vim ~/.aws/config
```

### Dataset Preparation
Let's produce `roosts-v0.1.0.json` to check whether the installation is successful.
- This repository already includes split v0.1.0 in `static/splits`
- This repository already includes `static/annotations/v1.0.0/user_annotations.txt` whose source is
[here](https://www.dropbox.com/s/0j9srf0jt6lc76e/user_annotations.txt?dl=0)
- `cd` into the `tools` directory and run `python prepare_dataset_v0.1.0.py`
- The generated `datasets/roosts-v0.1.0.json` should be the same as `datasets/roosts-v0.1.0-official.json` 
which is provided for reference as part of this repository

To produce a customized dataset, place customized split definitions and annotations under 
`static/splits` and `static/annotations`. Then modify `prepare_dataset_v0.1.0.py` and run it under `tools`.

### Dataset Visualization
There are two ways to visualize data.
1. Run `tools/visualization.ipynb` to interactively (1) render and visualize a scan or 
    (2) visualize channels from a npy array with its annotations from a json file.
    - Run `pip3 install jupyter` to install jupyter
    - Add the python environment to jupyter: 
        ```bash
        conda install -c anaconda ipykernel
        python -m ipykernel install --user --name=ENV
        ```
    - To check which environments are in jupyter as kernels and to delete one:
        ```bash
        jupyter kernelspec list
        jupyter kernelspec uninstall ENV
        ```
    - Run jupyter notebook on a server: `jupyter notebook --no-browser --port=9999`
    - Monitor from local: `ssh -N -f -L localhost:9998:localhost:9999 username@server`
    - Enter `localhost:9998` from a local browser tab to run the jupyter notebook interactively;
      the notebook should be self-explanatory.
2. `tools/visualization.py`, given a scan list file and a json file, can generate png images that 
    visualizes channels from npy arrays of the scans with annotations from the json file.

### References
[1] [Detecting and Tracking Communal Bird Roosts in Weather Radar Data.](https://people.cs.umass.edu/~zezhoucheng/roosts/radar-roosts-aaai20.pdf)
Zezhou Cheng, Saadia Gabriel, Pankaj Bhambhani, Daniel Sheldon, Subhransu Maji, Andrew Laughlin and David Winkler.
AAAI, 2020 (oral presentation, AI for Social Impact Track).