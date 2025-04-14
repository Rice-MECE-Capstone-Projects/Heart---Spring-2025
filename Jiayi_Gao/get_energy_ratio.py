import numpy as np
from scipy.signal import welch

fre_Low=[24,144]
fre_High=[200,500]
fre_Midd=[144,200]


def get_energy_ratio(x, fre, fs):
    nfft = round(fs)
    f, px = welch(x, fs=fs, nperseg=nfft, nfft=nfft)
    # Find indices within the specified frequency range
    ind = np.where((f >= fre[0]) & (f <= fre[1]))[0]
    # Avoid division by zero
    ratio = np.sum(px[ind]) / (np.sum(px) + np.finfo(float).eps)

    return ratio