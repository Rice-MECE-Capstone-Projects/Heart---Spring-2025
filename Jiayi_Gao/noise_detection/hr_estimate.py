import numpy as np
from scipy.linalg import svd
from scipy.signal import correlate, hilbert

from envelope import normalize_envelope


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
    from itertools import chain
    # fine search
    if est_period/fs*2 < 1.2:
        low_period = (est_period / fs - 0.1) * fs
        high_period = (est_period / fs + 0.1) * fs
        low_period_2 = (est_period*2 / fs - 0.2) * fs
        high_period_2 = (est_period*2 / fs + 0.2) * fs
        for i in chain(range(int(low_period), int(high_period + 0.1 * fs), int(0.01 * fs)),range(int(low_period_2), int(high_period_2 + 0.1 * fs), int(0.01 * fs))):
            stacked_signal = reshape_matrix(signal, i)
            tmp_phi = SVD_eva(stacked_signal)
            #print(tmp_phi,i/fs)
            if tmp_phi < min_phi:
                est_period = i
                min_phi = tmp_phi
    elif est_period/fs/2 > 0.4:
        low_period = (est_period / fs - 0.1) * fs
        high_period = (est_period / fs + 0.1) * fs
        low_period_2 = (est_period /2 / fs - 0.1) * fs
        high_period_2 = (est_period /2 / fs + 0.1) * fs
        for i in chain(range(int(low_period), int(high_period + 0.1 * fs), int(0.01 * fs)),
                       range(int(low_period_2), int(high_period_2 + 0.1 * fs), int(0.01 * fs))):
            stacked_signal = reshape_matrix(signal, i)
            tmp_phi = SVD_eva(stacked_signal)
            # print(tmp_phi,i/samplerate)
            if tmp_phi < min_phi:
                est_period = i
                min_phi = tmp_phi
    else:
        low_period = (est_period / fs - 0.1) * fs
        high_period = (est_period / fs + 0.1) * fs
        for i in range(int(low_period), int(high_period + 0.1 * fs), int(0.01 * fs)):
            stacked_signal = reshape_matrix(signal, i)
            tmp_phi = SVD_eva(stacked_signal)
            # print(tmp_phi,i/samplerate)
            if tmp_phi < min_phi:
                est_period = i
                min_phi = tmp_phi
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



def pre_find_hr(signal,fs):
    sig_half=signal[0:int(len(signal)/2)]
    envelop=np.abs(hilbert(signal))
    envelop_half=np.abs(hilbert(sig_half))
    normalized=normalize_envelope(envelop)
    normalized_hlf=normalize_envelope(envelop_half)
    corr=np.correlate(normalized,normalized,mode="full")
    corr_half=np.correlate(normalized_hlf,normalized_hlf,mode="full")
    print(find_hr_single_peak(corr_half,fs))
    print(find_hr_single_peak(corr,fs))
    print(find_hr_SVD(corr,fs))
    print(find_hr_SVD(corr_half,fs))
    return find_hr_single_peak(corr,fs)