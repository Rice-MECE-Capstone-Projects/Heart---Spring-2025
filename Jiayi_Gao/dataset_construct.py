import os

import numpy as np

from get_feature import get_feature, ori_data
from scipy.io import wavfile
import pandas as pd
def load_wav(wav_path):
    sample_rate, data = wavfile.read(wav_path)
    return sample_rate, data



# construct dataset first

df=pd.read_csv('quality_label.csv')
second_col = df.iloc[:, 1]
label = np.where(second_col.isin([4, 5]), 0, 1)
wav_dir="D:\\Rice_25spring\\594\\heart_sound_database_for_quality_assessment\\data_for_open"


wav_files = sorted(
    [f for f in os.listdir(wav_dir) if f.endswith(".wav")],
    key=lambda x: int(os.path.splitext(x)[0])  # extracts the number
)
features=np.zeros((len(wav_files), 10))
for i, filename in enumerate(wav_files):
    filepath = os.path.join(wav_dir, filename)
    print(filename)
    ori_fs, ori_data = wavfile.read(filepath)
    features[i] = get_feature(ori_data, ori_fs)


np.savez("dataset_bin.npz",data=features,target=label)
