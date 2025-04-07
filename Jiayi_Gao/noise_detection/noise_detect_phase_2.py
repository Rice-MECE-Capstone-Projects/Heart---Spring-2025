import numpy as np
from scipy.signal import ShortTimeFFT

# spectral energy
def stft_win(signal,fs):
    N=len(signal)
    win=np.hanning(N)
    for i in range(N):
        if i > N/2:
            win[i]=0
    SFT=ShortTimeFFT(win=win,fs=fs,hop=1)
    STFT=np.abs(SFT.stft(signal))
    return STFT
def root_mean_square(stft):
    s_rms=np.zeros(stft.shape[0])
    for i in range(stft.shape[0]):
        s_rms[i]=np.sqrt(np.sum(stft[i]**2))
    return s_rms
def srms_evaluate(ref,test,fs):
    ref_stft=stft_win(ref,fs)
    test_stft=stft_win(test,fs)
    ref_rms=root_mean_square(ref_stft)
    test_rms=root_mean_square(test_stft)
    coef=np.corrcoef(ref_rms,test_rms)[0][1]
    if coef>0.98:
        print("Segment passed spectral RMS test")
        return True
    else:
        print("Segment failed spectral RMS test, correlation coefficient:",coef)
        return False
# temporal energy
def ref_max_te(ref,fs):
    tw=int(0.05*fs)
    max_te=0
    for i in range(0,len(ref),int(tw)):
        te=np.sum([x**2 for x in ref[i:i+tw]])
        if te>max_te:
            max_te=te
    return max_te
def test_rte(test,fs,ref_te):
    tw=int(0.05*fs)
    rte=np.zeros(int(len(test)//tw))
    for i in range(0,rte.shape[0]):
        rte[i]=np.sum([x**2 for x in test[i*tw:i*tw+tw]])/ref_te
    return rte
def te_evaluate(rte):
    for r in rte:
        if r>3:
            print("failed temporal energy test with relative temporal energy ",r)
            return False
    print("passed temporal energy test")
    return True

