import numpy as np
from scipy.linalg import svd
from scipy.signal import correlate

def SVD_eva(m):
    theta=svd(m,compute_uv=False)
    phi=(theta[1]/theta[0])**2
    return phi
def reshape_matrix(signal,n):
    m=len(signal) // n
    return [signal[i * n : (i + 1) * n] for i in range(m)]
def find_hr_SVD(signal,fs):
    low_period=0.4*fs
    high_period=1.2*fs
    min_phi=1
    est_period=0
    # coarse search
    for i in range(int(low_period),int(high_period+0.1*fs),int(0.1*fs)):
        stacked_signal=reshape_matrix(signal,i)
        tmp_phi=SVD_eva(stacked_signal)
        #print(tmp_phi,i/fs)
        if tmp_phi < min_phi:
            est_period=i
            min_phi=tmp_phi
    #print("coarse search heart cycle ",est_period/fs,"s")
    # fine search
    low_period=(est_period/fs-0.1)*fs
    high_period=(est_period/fs+0.1)*fs
    for i in range(int(low_period),int(high_period+0.1*fs),int(0.01*fs)):
        stacked_signal=reshape_matrix(signal,i)
        tmp_phi=SVD_eva(stacked_signal)
        #print(tmp_phi,i/samplerate)
        if tmp_phi < min_phi:
            est_period=i
            min_phi=tmp_phi
    return est_period/fs


# heart rate estimation using single peak algorithm from "Robust Heart Rate Estimation from Noisy Phonocardiograms"
from scipy.signal import find_peaks



def find_hr_single_peak(corr,fs):
    low_period=int(60/140*fs)
    high_period=int(60/50*fs)
    segment=corr[low_period:high_period]
    peaks,property=find_peaks(segment)
    #print(peaks)
    highest_peak = peaks[np.argmax(segment[peaks])]
    value=segment[highest_peak]
    lag_time=highest_peak/fs+60/140
    return lag_time