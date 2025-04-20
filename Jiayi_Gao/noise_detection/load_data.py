# function for loading and preprocessing data
from scipy.io import wavfile
import numpy as np
from scipy.signal import decimate


def load_wav(wav_path):
    sample_rate, data = wavfile.read(wav_path)
    return sample_rate, data
def pre_process(data):
    R=3
    data=data/np.std(data)
    abs_data_sorted=-np.sort(-1*np.abs(data))# sort in descending order
    TH=np.mean(abs_data_sorted[0:int(0.1*len(data))])
    for i in range(0,len(data)):
        if np.abs(data[i]) > R*TH:
            data[i] = R*TH
    data=data/np.std(data)
    return data

def down_sample(signal, fs):
    target_fs = 2000
    decimation_factor = int(fs / target_fs)
    if fs % target_fs != 0:
        raise ValueError("Original sampling rate must be an integer multiple of 1000 Hz.")
    # Use decimate with FIR filter for better quality (zero-phase by default)
    downsampled_signal = decimate(signal, decimation_factor, ftype='fir', zero_phase=True)
    return downsampled_signal

