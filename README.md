# wsrdata
Weather surveillance radar archives hold detailed information about biological phenomena in the atmosphere.
Given radar scan lists, annotations, and specifications, this repository prepares datasets for training and evaluating 
machine learning models for detecting and tracking communal bird roosts. 

### Under Construction
- install the dataset to Detectron2
- more functionality for the API; refer to [COCO API](https://github.com/cocodataset/cocoapi)
- maybe [HDF5](https://docs.h5py.org/en/stable/quick.html) to store arrays
- pyart rendering [issue](https://github.com/darkecology/wsrdata/issues/1);
as of now, need to manually make sure the split json files do not contain scans with rendering exceptions since
some array paths in the json may be invalid due to those exceptions

### Repo Overview
- **datasets** stores dataset definitions that are prepared by this repository.
    - **datasets/roosts_v0.0.1_official** defines a toy dataset for reference.
        - **roosts_v0.0.1.json** is in a modified [COCO format](https://cocodataset.org/#format-data) and
        human-readable with line indentation of 4. It defines a dataset based on or referring to:
            1. the scan list **static/scan_lists/v0.0.1/scan_list.txt**, 
            2. arrays in **static/arrays/v0.0.1**,
            3. annotations from **static/annotations/v1.0.0/user_annotations.txt**, and
            4. bounding box scaling factors from
            **static/user_models/v1.0.0/hardEM200000_user_models_python2.pkl** for alleviating annotator biases.
        - **roosts_v0.0.1_standard_splits.json** defines a train/test split according to 
        **static/scan_lists/v0.0.1/v0.0.1_standard_splits/{train,test}.txt** and complements **roosts_v0.0.1.json** 
        which does not specify splits.
        - **visualization** contains images that visualize scans with bounding boxes.
        The images are generated by **tools/visualization.py**.

- **src/wsrdata** implements functions relevant to dataset preparation and analyses:
    - **download_radar_scans.py** downloads radar scans
    - **render_npy_arrays.py** uses pywsrlib to render arrays from radar scans and save them
    - **utils** contains utility/help functions

- **static** contains static files that are inputs to the dataset preparation pipeline or 
generated during the preparation (see the following Release section for more info):
    - **scan_lists** is for different versions of scan lists and splits
    - **scans** is for downloaded radar scans
    - **arrays** is for different versions of arrays rendered from scans, 
    each version corresponding to a certain set of rendering configs
    - **annotations** is for different versions of annotations
        - As of 4/20/2021, there is only one set of csv annotations **v1.0.0/user_annotations.txt**. 
        If in the future there is a new input format for annotations, related code including that in 
        step 6 of **tools/prepare_dataset_\*.py** will need to be updated.
    - **user_models** is for different versions of bounding box scaling factors learned by 
    an EM algorithm [1] to alleviate annotator biases

- **tools** contains scripts to run the data preparation pipeline and visualization:
    - **prepare_dataset_v0.0.1.py** is a modifiable template that prepares the toy dataset v0.0.1; it
     downloads radar scans, renders arrays, reads annotations, and creates json files that define the dataset.
     See the following Dataset Preperation section for detailed steps.
    - prepare_dataset_v0.1.0: See **prepare_dataset_v0.1.0_help/README.md** for steps.
    - **visualization.py** generates png images that visualize selected channels in rendered arrays for 
    a given list of scans with annotations from a designated json file.
    - **visualization.ipynb** can interactively (1) render an array from a scan and visualize it and
    (2) visualize selected channels from a rendered array with its annotation(s) from a json file.
    - **generate_img_for_ui** generates images for the web interface.
    - **json_to_csv.py** generates csv files from json (for the web interface).

- _**Important notes:**_
    - By default pywsrlib renders arrays in the geographical direction;
    i.e. when calling `radar2mat`, `ydirection='xy'` by default.
    In the rendered array, y is the first dimension and x the second.
    Large y indicates North and large x indicates East. For visualization using matplotlib's `imshow`, 
    we need to set `origin='lower'` in order that North is the top of the image.
    When saving images from array channels for UI, we manually flip the y axis of the arrays and annotations.
    - As of now this repo renders arrays with `ydirection='xy'`.
    - Although not the case in this repo, if `ydirection='ij'`, large y will indicate South.
    Then for visualization using matplotlib's `imshow`, 
    the default `origin=None` will correspond to images with North as the top.    

### Release
#### datasets
- **roosts_v0.0.1** uses arrays v0.0.1, annotations v1.0.0, and user_models v1.0.0_hardEM200000.
- **roosts_v0.1.0** uses arrays v0.1.0, annotations v1.0.0, and user_models v1.0.0_hardEM200000.

#### scan_lists
- **v0.0.1** has 6 scans and can be used to test whether the dataset preparation pipeline is successfully set up.
    - **v0.0.1_standard_splits** has 3 scans in train.txt and test.txt respectively.
- **v0.1.0** contains 88972 scans used in [1].
    - **v0.1.0_subset_for_debugging** is generated by **pick_scans_to_visualize.py** and
    can be used to visualize and examine a random subset of the dataset by annotation-station.
    - **v0.1.0_randomly_ordered_splits**, which is used in [1], splits all scans by day-station, i.e. 
    scans from the same day at the same station. Scans are randomly ordered in the txt files.
        - **train.txt**: 53600 scans, among which 26895 are in annotation v1.0.0, ~60.24%
        - **val.txt**: 11658 scans, among which 3796 are in annotation v1.0.0, ~13.10%
        - **test.txt**: 23714 scans, among which 7711 are in annotation v1.0.0, ~26.65%
    - **v0.1.0_ordered_splits** is the same as the **v0.1.0_random_order**, except that 
    the scans are alphabetically ordered in the txt files.
    - **v0.1.0_standard_splits** is the same as **v0.1.0_ordered_splits** except that scans with rendering 
    errors are removed.
        - **train.txt**: 53266 scans
        - **val.txt**: 11599 scans
        - **test.txt**: 23587 scans

#### arrays
- **v0.0.1** and **v0.1.0**
    - "array": _{reflectivity, velocity, spectrum_width}_ x _elevations{0.5, 1.5, 2.5, 3.5, 4.5}_ x 600 x 600.
    - "dualpol": _{differential_reflectivity, cross_correlation_ratio, differential_phase}_ x 
    _elevations{0.5, 1.5, 2.5, 3.5, 4.5}_ x 600 x 600.

#### annotations
- **v1.0.0** is a txt file and can be downloaded 
[here](https://www.dropbox.com/s/0j9srf0jt6lc76e/user_annotations.txt?dl=0).
Notice that the second column can end with ".gz" or ".Z". 
Previous to this repository, the list was processed to become *.mat files 
[here](https://www.dropbox.com/s/eti469m1z4634x4/Annotations.zip?dl=0) and used by [1]. 
Refer to [this sheet](https://docs.google.com/spreadsheets/d/1lvEWNSSJsT9WYGgUE3rIkOoy9vU2zHEPTCiVJnRdFaI/edit)
for annotator information.

#### user_models
- **v1.0.0** can be found [here](https://www.dropbox.com/sh/d3ronsvzr9c0xxq/AAD9fgrk2exRuyWcBjtU7Ea8a?dl=0),
where the pkl files can be loaded by python 2 but not python 3. User models are bounding box scaling factors learned
by EM. Consider outputs of Faster RCNN in [1] as ground truth: User factor = biased user annotation / ground truth.
User factors are currently manually imported to `tools/prepare_dataset_v0.0.1.py`.

    
### Installation
Create and activate a python 3.6 environment. Check the cuda version at, for example, `/usr/local/cuda`, 
or potentially by `nvcc -V`. While many versions should workd, we use cuda 10.1. 
Install a compatible version of [PyTorch](https://pytorch.org/get-started/previous-versions/).
```bash
conda create -n roost2021 python=3.6
conda activate roost2021
pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
```

Assume we are under a roost project directory `roosts`. Let's create a `libs` directory where
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

[Configure AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) by
`aws configure`
in order to download radar scans. 
Enter `AWS Access Key ID` and `AWS Secret Access Key` as prompted,
`us-east-1` for `Default region name`, and nothing for `Default output format`.
Review the updated AWS config.
```bash
vim ~/.aws/credentials
vim ~/.aws/config
```

### Dataset Preparation
Let's produce `roosts_v0.0.1.json` to check whether the installation is successful.
- `cd` into the `tools` directory and run `python prepare_dataset_v0.0.1.py`
- The generated `roosts_v0.0.1.json` and `roosts_v0.0.1_standard_splits.json` under 
`datasets/roosts_v0.0.1/` should be the same as those under `datasets/roosts_v0.0.1_official/`
which are provided for reference as part of this repository

`tools/prepare_dataset_v0.1.0.py` defines a much larger dataset. 
`tools/prepare_dataset_v0.1.0_help` contains optional helper functions that are useful for accelerating 
the dataset creation and checking the correctness of the creation process; 
see the README in that directory for details.

To produce a customized dataset, place customized scan lists, annotations, and user models under
`static`. Then modify `prepare_dataset_v0.1.0.py` and run it under `tools`.

### Dataset Visualization
There are two ways to visualize data.
1. Run `tools/visualization.ipynb` to interactively (1) render and visualize a scan or 
    (2) visualize channels from an array with its annotations from a json file.
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
    visualizes selected channels from arrays rendered from the scans with annotations from the json file.

### References
[1] [Detecting and Tracking Communal Bird Roosts in Weather Radar Data.](https://people.cs.umass.edu/~zezhoucheng/roosts/radar-roosts-aaai20.pdf)
Zezhou Cheng, Saadia Gabriel, Pankaj Bhambhani, Daniel Sheldon, Subhransu Maji, Andrew Laughlin and David Winkler.
AAAI, 2020 (oral presentation, AI for Social Impact Track).