# wsrdata
Weather surveillance radar archives hold detailed information about biological phenomena in the atmosphere.
Given radar scans and specifications, this repository prepares datasets for training and evaluating 
machine learning models for detecting and tracking communal bird roosts. 

#### Overview
- **datasets** is a directory reserved for json files created by this repository to define datasets 
in the [COCO format](https://cocodataset.org/#format-data).
We use 0-based indexing for all ids; empty lists, empty strings, and -1 to indicate "not applicable".
    - To give a specific example, **roosts-v1.0.0.json** can be formatted as follows.
    ```angular2
    {
        "info":           info,
        "license":        [license],
        "arrays":         {"train": [array],
                           "val": [array],
                           "test": [array]},
        "categories":     ["roost", "rain", ...],
        "annotations":    {"train": [annotation],
                           "val": [annotation],
                           "test": [annotation]},
    }
  
    info = {
        "description":          "A roost dataset with bbox annotations.",
        "url":                  "",
        "version":              "v1.0.0",
        "split_version":        "v1.0.0",
        "annotation_version":   "v1.0.0",
        "data_created":         "yyyy/mm/dd",
        "array_shapes":         [(600, 600, 16)],
        "channels":             [("reflectivity", 0.5),
                                 ("radial_velocity", 0.5),
                                 ("spectrum_width", 0.5),
                                 ...,
                                 ("dual_pol")],
    }
  
    license = {
        "id":     int,
        "name":   str,
        "url":    str,
    }
  
    array = {
        "id":                 int,
        "path":               str,
        "license_id":         int,
        "scan":               str,
        "array_shape_id":     int,
    }
    
    annotation = {
        "id":                     int,
        "array_id":               int,
        "category_id":            int,
        "bbox":                   [x, y, width, height],
        "bbox_annotator":         str,
        "bbox_scaling_factor":    float,
        "segmentation":           [polygon],
        "segmentation_annotator": str,
    }
    ```

- **src/wsrdata** implements functions used for dataset preparation:
    - **download_radar_scans.py** downloads radar scans whose radius is typically 150km for US radar stations
    - **render_npy_arrays.py** renders npy arrays from radar scans using the 
    [pywsrlib](https://raw.githubusercontent.com/darkecology/pywsrlib) toolkit
    - **create_dataset.py** creates json files which define datasets, as illustrated
    - **format_dataset.py** converts json to and from csv, which can be input to web interfaces
    - **visualize_data.py** generates images for a selected channel in npy arrays 
    with annotations extracted from json

- **static** contains static files that are inputs to the dataset preparation pipeline or 
generated during the preparation:
    - **scans** is reserved for downloaded radar scans
    - **splits** is reserved for different versions of data splits
        - **v1.0.0**, as an example, contains **train/val/test.txt**, each a scan list
    - **arrays** is reserved for npy arrays rendered from scans according to splits
        - **600x600x16**, as an example, stores 600x600x16 arrays where the 16 channels are 
        {reflectivity, radial velocity, spectrum width} x 5 elevations + dual_pol 
        (i.e. copolar cross-correlation coefficient which is available since 2013)
    - **annotations** is reserved for different versions of annotations
        - **v0.1.0**, for example, is for .mat files downloaded from 
         [here](https://www.dropbox.com/s/eti469m1z4634x4/Annotations.zip?dl=0)
    
- **tools** contains scripts that call functions from **src/wsrdata** to 
partially or entirely run the dataset preparation pipeline:
    - **prepare_dataset_v0.1.0.py** is a modifiable template that, given metadata, can be called to
    download radar scans, render npy arrays, and create json files which define datasets
    - **run_download_radar_scans.py** can be called download scans by scan, station, city, region, or
    other specifications

#### Release
There are 2 official versions:
- **v0.1.0** involves 3 scans in the train and test splits respectively and 
can be used to test whether the codebase is successfully set up
- **v1.0.0** is the split used to train the detection model in 
*Detecting and Tracking Communal Bird Roosts in Weather Radar Data (Cheng et al. 2020)*
and involves 88972 scans, including 53600 (~60.24%) for train, 11658 (~13.10%) for val, 23714 (~26.65%) for test

#### Installation
Create and activate a python 3.6 environment. Check the cuda version at, for example, `/usr/local/cuda`, 
or potentially by `nvcc -V`. We use cuda 10.1. 
Install a compatible version of [PyTorch](https://pytorch.org/get-started/previous-versions/).
```bash
conda create -n roost2021 python=3.6
conda activate
pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
```

Enter some roost project directory within which we will create `libs` to install the pywsrlib toolkit and 
data preparation functions implemented in this repository. 
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
