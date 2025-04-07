import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import ShortTimeFFT
def fre_bands_spectrum(signal,fs):
    N=len(signal)
    win=np.hanning(N)
    for i in range(N):
        if i > N/2:
            win[i]=0
    SFT=ShortTimeFFT(win=win,fs=fs,hop=1)
    STFT=SFT.stft(signal)
    y_lo=int((STFT.shape[1]+1)/4)
    y_hi=int((STFT.shape[1])*0.75)
    fre_limit=int(np.floor(600/(fs/2)*SFT.f_pts))
    temp=STFT[:fre_limit,y_lo:y_hi]
    tmp=temp.reshape(15,int(temp.shape[0]/15),temp.shape[1]).sum(axis=1)
    fre_bands=np.zeros((15,tmp.shape[1]))
    for i in range(15):
        fre_bands[i]=[np.abs(j)**2 for j in tmp[i]]


    return fre_bands

def get_auto_cor_bands(fre_bands):
    as_k_len = 2 * fre_bands.shape[1] - 1
    as_k = np.zeros((15, as_k_len))
    as_k_tmp=   np.zeros((15, fre_bands.shape[1]))
    for i in range(15):
        as_k[i] = np.correlate(fre_bands[i], fre_bands[i], mode="full")
        as_k_tmp[i]=as_k[i][:fre_bands.shape[1]]
    return as_k_tmp