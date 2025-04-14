import numpy as np
from scipy.signal import spectrogram, butter, filtfilt
from pre_processing import remove_spike
import numpy as np
from scipy.spatial.distance import pdist
def get_envelope_from_stft(phs, fs):
    win_length = int(0.03 * fs)
    win = np.ones(win_length)
    noverlap = win_length - 1
    nfft = fs
    # Compute STFT using spectrogram
    f, t, s = spectrogram(phs, fs=fs, window=win, noverlap=noverlap, nfft=nfft, mode='complex')
    # Smoothed magnitude (average across frequency bins)
    ins_fre_raw = np.sum(np.abs(s), axis=0) / nfft
    # Low-pass filter (Butterworth)
    fc = 20  # Hz
    b, a = butter(N=3, Wn=2 * fc / fs, btype='low')
    ins_fre = filtfilt(b, a, ins_fre_raw)
    # Remove spikes
    envelope = remove_spike(ins_fre)
    return envelope

def get_envelop_sample_entropy(x,m,r):
    """
    Fast Sample Entropy (SampEn) using Chebyshev distance.

    Parameters:
    x : 1D numpy array, the input time series
    m : embedding dimension
    r : tolerance (usually r = 0.1 ~ 0.25 * std)

    Returns:
    SampEn : Sample Entropy value
    """

    x = np.asarray(x).flatten()  # Ensure 1D
    x = (x - np.mean(x)) / np.std(x)  # z-score normalization
    N = len(x)

    # Create embedding matrices using Hankel structure
    indm = np.array([x[i:i + m] for i in range(N - m)])
    inda = np.array([x[i:i + m + 1] for i in range(N - m)])

    # Compute Chebyshev distances
    cheb_m = pdist(indm, metric='chebychev')
    cm = np.sum(cheb_m <= r) * 2 / (len(indm) * (len(indm) - 1) + np.finfo(float).eps)

    cheb_a = pdist(inda, metric='chebychev')
    ca = np.sum(cheb_a <= r) * 2 / (len(inda) * (len(inda) - 1) + np.finfo(float).eps)

    # Compute Sample Entropy
    sampen = -np.log(ca / (cm + np.finfo(float).eps))

    return sampen
