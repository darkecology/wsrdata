# wsrdata
Weather surveillance radar archives hold detailed information about biological phenomena in the atmosphere.
Given radar scan lists, annotations, and specifications, this repository prepares datasets for training and evaluating 
machine learning models for detecting and tracking communal bird roosts. 

### Repo Overview
- **datasets** stores dataset definitions that are prepared by this repository.
    - **datasets/roosts_v0.0.1_official** defines a toy dataset for reference. 
    It is generated by **tools/prepare_dataset_v0.0.1.py** described below.
    Notice that various fields can be added in new dataset versions.
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
    - **datasets/roosts_v0.0.2_official** is similar.
        It is generated by **tools/prepare_dataset_v0.0.2.py** described below.

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
        - As of 12/31/2021, **v2.0.0** contains ecologist-screened roost-system predictions for 12 great lakes stations.
    - **user_models** is for different versions of bounding box scaling factors learned by 
    an EM algorithm [1] to alleviate annotator biases

- **tools** contains scripts to run the data preparation pipeline and visualization:
    - **analyze_screened_data.ipynb** is a notebook from Maria our CSU colleague for calculating stats from 
    csv files resulting from screening.
    - **prepare_dataset_v0.0.1.py** is a modifiable template that prepares the toy dataset v0.0.1; it
     downloads radar scans, renders arrays, reads annotations, and creates json files that define the dataset.
     The scans and annotations in the json are 0-indexed.
     See the following Original Dataset Preperation section for detailed steps.
    - prepare_dataset_v0.1.0 is based on the above template and generates the dataset in [1] in the COCO format.
    See **prepare_dataset_v0.1.0_help/README.md** for details.
    - preparing dataset_v0.2.B involves three scripts. See the 
    [documentation](https://docs.google.com/document/d/1zX8Sa2hVvjWBhFXQg124XRX1laKY-3aK43dDJLLlD0I/edit?usp=sharing) 
    for details.
        - **organize_screened_csv_as_json.py** organizes scans and annotations from multiple years of a station, 
        calculates stats of ecologist-screened roost-system predictions, and save them as json.
        - **create_splits_from_organized_json.py** reads the json created from csv output by the UI and 
        defines scan lists and splits under **static/scan_lists/{version}**.
        - **prepare_dataset_{v0.0.2, v0.2.0}.py**: prepares a dataset that contains dataset {v0.0.1, v0.1.0} and also 
        ecologist-screened roost-system predictions. This script does not scale the screened annotations by user models.
        This script doesn't check for duplications; 
        need to make sure the same scan doesn't appear in multiple versions manually.
    - **visualization.py** generates png images that visualize selected channels in rendered arrays for 
    a given list of scans with annotations from a designated json file.
    - **visualization.ipynb** can interactively (1) render an array from a scan and visualize it and
    (2) visualize selected channels from a rendered array with its annotation(s) from a json file.
    - **tmp** is for files temporarily needed for development or sanity check but not dataset preparation.
    - **generate_img_for_ui.py** generates images for the web interface.
    - **json_to_csv.py** generates csv files from json for the web interface.

- _**Important notes:**_
    - By default pywsrlib renders arrays in the geographical direction;
    i.e. when calling `radar2mat`, `ydirection='xy'` by default.
    In such rendered arrays, y is the first dimension and x the second.
    Large y indicates North and large x indicates East. 
    As of now this wsrdata repo renders arrays with `ydirection='xy'`.
    Annotations v1.0.0 in this repo also uses `ydirection='xy'`.
    To visualize the array channels using matplotlib's `pyplot.imshow`, 
    we need to set `origin='lower'` in order that North is the top of the image.
    Before saving images of array channels for UI using matplotlib's `image.imsave`, 
    we need to manually flip the y axis of the arrays and annotations v1.0.0 in order that 
    North is the top of the image.
    - Although not the case in this wsrdata repo, if rendering with `ydirection='ij'`, large y will indicate South.
    Flip the y axis of annotations so that they correspond to the rendered arrays.
    To visualize the array channels using matplotlib's `pyplot.imshow`, 
    the default `origin=None` will yield images with North as the top.

### Release
#### datasets
- v0.0.A are mini-datasets for demo; 
v0.A.B are development datasets, A is annotation version, B indicates sampling strategies.
- user_models are for scaling bounding boxes since annotators may differ in style; no user_models is used by default.
- **roosts_v0.0.1** uses arrays v0.0.1, annotations v1.0.0, and user_models v1.0.0_hardEM200000.
- **roosts_v0.0.2** uses arrays v0.0.2, annotations v2.0.0, in addition to everything from roosts_v0.0.1.
- **roosts_v0.1.0** uses arrays v0.1.0, annotations v1.0.0, and user_models v1.0.0_hardEM200000.
- **roosts_v0.2.B** uses arrays v0.2.0, annotations v2.0.0, in addition to everything from roosts_v0.1.0. See the 
    [documentation](https://docs.google.com/document/d/1zX8Sa2hVvjWBhFXQg124XRX1laKY-3aK43dDJLLlD0I/edit?usp=sharing) 
    for preparation details.

#### scan_lists
- **v0.0.1** has 6 scans and can be used to test whether the dataset preparation pipeline is successfully set up.
    - **v0.0.1_standard_splits** has 3 scans in train.txt and test.txt respectively.
- **v0.0.2** is similar.
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
    - **v0.1.0_KDOX_splits** is a subset of **v0.1.0_standard_splits** with only KDOX scans.
- **v0.2.B** has scan lists from 12 great lakes stations.

#### arrays
- **v0.0.1**, **v0.1.0**, **v0.2.B**
    - "array": _{reflectivity, velocity, spectrum_width}_ x _elevations{0.5, 1.5, 2.5, 3.5, 4.5}_ x 600 x 600.
    - "dualpol": _{differential_reflectivity, cross_correlation_ratio, differential_phase}_ x 
    _elevations{0.5, 1.5, 2.5, 3.5, 4.5}_ x 600 x 600.

#### annotations
- **v1.0.0** is a txt file and can be downloaded 
[here](https://www.dropbox.com/s/0j9srf0jt6lc76e/user_annotations.txt?dl=0).
In the file, y and x are in the range of -150000 to 150000 meters. 
Large y indicates North; large x indicates East.
Notice that the second column can end with ".gz" or ".Z". 
Previous to this repository, the list was processed to become *.mat files 
[here](https://www.dropbox.com/s/eti469m1z4634x4/Annotations.zip?dl=0) and used by [1]. 
Refer to [this sheet](https://docs.google.com/spreadsheets/d/1lvEWNSSJsT9WYGgUE3rIkOoy9vU2zHEPTCiVJnRdFaI/edit)
for annotator information.
- **v2.0.0** contains annotations for 12 great lakes stations predicted by roost-system with detector
`07/logs/resnet101-FPN_detptr_anc10_regsl1_imsz1200_lr0.001_it150k/model_0039999.pth` and 
screened by our CSU ecology colleagues.

#### user_models
- **v1.0.0** can be found [here](https://www.dropbox.com/sh/d3ronsvzr9c0xxq/AAD9fgrk2exRuyWcBjtU7Ea8a?dl=0),
where the pkl files can be loaded by python 2 but not python 3. User models are bounding box scaling factors learned
by EM. Consider outputs of Faster RCNN in [1] as ground truth: User factor = biased user annotation / ground truth.
User factors are currently manually imported to `tools/prepare_dataset_v0.0.1.py`.

    
### Installation
```bash
conda create -n roost2021 python=3.6
conda activate roost2021
git clone https://github.com/darkecology/wsrdata.git
pip install -e wsrdata
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

Optional installation for jupyter notebook functionalities.
- Run `pip install jupyter` to install jupyter
- Add the python environment to jupyter. Replace `ENV` by `roost2021` in our case.
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
     
### Original Dataset Preparation
Inside our `wsrdata` repo, let's produce `datasets/roosts_v0.0.1.json` to check whether the installation is successful.
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
2. `tools/visualization.py`, given a scan list file and a json file, can generate png images that 
    visualizes selected channels from arrays rendered from the scans with annotations from the json file.

### Potential Future Work
- remove duplicated annotations by more than one annotator from **annotations v1.0.0**
- more functionality for the API; refer to [COCO API](https://github.com/cocodataset/cocoapi)
- maybe [HDF5](https://docs.h5py.org/en/stable/quick.html) to store arrays
- pyart rendering [issue](https://github.com/darkecology/wsrdata/issues/1)

### References
[1] [Detecting and Tracking Communal Bird Roosts in Weather Radar Data.](https://people.cs.umass.edu/~zezhoucheng/roosts/radar-roosts-aaai20.pdf)
Zezhou Cheng, Saadia Gabriel, Pankaj Bhambhani, Daniel Sheldon, Subhransu Maji, Andrew Laughlin and David Winkler.
AAAI, 2020 (oral presentation, AI for Social Impact Track).