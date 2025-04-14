import numpy as np
import pywt

wavelet='db10'
level=4

def soft_thresholding(data, threshold):
    return np.sign(data) * np.maximum(np.abs(data) - threshold, 0)



def pre_denoise(signal,fs):
    coeffs=pywt.wavedec(signal,wavelet=wavelet,level=level)
    threshold=np.median(np.abs(coeffs[-1])) / 0.6745 * np.sqrt(2 * np.log(len(signal)))
    denoised_coeffs = [soft_thresholding(c, threshold) if i > 0 else c for i, c in enumerate(coeffs)]
    return pywt.waverec(denoised_coeffs, wavelet)