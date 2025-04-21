## Denoising Pipeline
This repo contains code associated with a neural network based denoising pipeline

### Repo Structure
- visuals: Directory containing a few plots
- physionet-exploration.ipynb: A short notebook where I got acquainted with exploring the Physionet 2016 dataset
- **u-net.ipynb**: The core of the notebook, and the file which contains the entire denoising pipeline

### A Guide to u-net.ipynb
This file is split into 9 sections. I'll go into each of them soon. First though, some general notes about the notebook:
- Every so often in the notebook I had an important design decision, note, or variable to highlight. What I did in these particularly important areas was leave a comment containing the string "!impt". To not miss these things, I'd highly recommend doing ctrl+F in the notebook for "!impt" (without quotes) to not miss any crucial information.
- The notebook assumes you have the following datasets installed locally: PASCAL, Physionet 2016, Physionet 2022, ARCA23K, ESC-50, HAN. If you have great interest in running this notebook locally, message me on Slack and I'll send you all of these datasets in the structure the notebook expects them to be in.
- The notebook itself is fairly heavily annotated and has frequent markdown headers explaining the purpose of each section and subsection of the model. There are several hundred comments. Besides this README, which exists to inform you what to expect,  I hope you will find that the pipeline notebook is fairly self-explanatory and easy to navigate and understand.
 
That is all for general information. Now, a guide to each section:
#### Section 0 - Introduction
This section contains imports, filepath definitions, and optionally setting environment variables if the notebook is being run on cloud GPUs. Ideally this should be the only section a user would need to edit if they ran this notebook.
#### Section 1 - Loading the Data
This section contains data exploration, mostly in pandas. Data is loaded in from all of the aforementioned datasets. Datasets are also trimmed here such that only their relevant parts are used later in the notebook. Especially w.r.t Physionet 2016, this is an important section as it determines which murmurs from that dataset get included in the training/val/test data later on.
#### Section 2 - Normalization
This section concerns creating a toolkit to modify and analyze single audio files with. Functions to load a signal from a filepath, filter a signal, resample a signal, and plot the spectrum of a signal are introduced here.
#### Section 3 - Signal Combination
This section concerns creating a toolkit to modify multiple audio files with. Functions to do things like match the lengths of two signals and combine two signals at a certain SNR are introduced here. Also defined here are functions to randomly fetch noise files from noise datasets are defined here, as are functions to measure the extend of noise contamination (such as RMSE and SNR measurements).
#### Section 4 - Making STFT Features
This is a legacy section which is currently no longer referenced anywhere else in the pipeline. However this section contains code for extracting frequency-domain representations of audio signals and associated features.  
#### Section 5 - Making Train/Val/Test Data
This section is dedicated to creating the training, validation and test data for the model. The following process was used to generate the data:

1. First, find all clean PCGs available in the PCG datasets, and split them into three groups of train/val/test data (the ratio 70/15/15 was used for this, at time of writing)

2. Second, the following process:
    1. For each clean PCG:
        1. For each SNR value in a list of SNR values:
            1. For each noise in a list of a+b+c noises ("a" noises from the HAN noise dataset, "b" from ARCA23k, and "c" from ESC-50):
               1. Combine the noise with the clean PCG at the SNR value
               2. Cut the clean PCG and the noise+clean PCG into fixed length segments
               3. Add the fixed length segments + relevant metadata (e.g. murmur presence) to either training, validation or test data
              
Numpy memmaps are used to store the data, to accommodate potentially very large datasets

#### Section 6 - Model Definition
In this section, model architectures are defined, along with optimizers, loss functions and schedulers. At time of writing there are two main models in this section
1. Lite_UNet: This is a U-Net inspired model except fairly short and without skip-connections
2. U_Net: This is more or less a typical U-Net model, except one dimensional.
#### Section 7 - Model Training
This section is where model training occurs, and also contains functions are written to measure weighted/unweighted validation loss as well as visualize the model's progression during training. Overfitting is measured in various ways (e.g. patience, rising validation loss, large gap between training and validation loss), using weighted validating loss.
#### Section 8 - Measuring Model Performance
This is the final section. It is where model performance is quantified (using RMSE pre and post running the model) on the training data, and where the model's denoising is visualized on a small subset of PCG recordings. 

### Conclusion
I hope this has been an insightful document and that it helps you better understand the flow of the denoising pipeline. Don't forget to ctrl+F for "!impt" to not miss anything though. 
