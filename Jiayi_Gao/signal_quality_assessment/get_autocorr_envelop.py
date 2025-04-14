import numpy as np
from scipy.signal import correlate
def get_autocorr_envelop(enve):
    enve = enve - np.mean(enve)
    # Full (double-sided) normalized autocorrelation
    axcor_enve_double_side = correlate(enve, enve, mode='full')
    axcor_enve_double_side = axcor_enve_double_side / np.max(axcor_enve_double_side)  # equivalent to 'coeff'
    mid = len(enve) - 1
    axcor_enve_single_side = axcor_enve_double_side[mid:]
    return axcor_enve_single_side

def get_max_autocorr_coeff(axcor,fs):
    start=int(np.round(fs*0.3))
    end=int(np.round(fs*2))
    return np.max(axcor[start:end])