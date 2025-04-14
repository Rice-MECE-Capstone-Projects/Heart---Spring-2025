import numpy as np
from scipy.signal import hilbert
from numpy.fft import fft, ifft




def fast_cfs(y, k, f1, f2, fs):
    """
    Fast computation of the Cycle Frequency Spectrum (CFS).

    Parameters:
    y  : input signal (1D array)
    k  : number of bins in cycle frequency domain
    f1 : lower bound of cycle frequency (Hz)
    f2 : upper bound of cycle frequency (Hz)
    fs : sampling frequency (Hz)

    Returns:
    g  : cycle frequency spectrum (complex values)
    """
    y = np.asarray(y).flatten()
    m = len(y)

    # Analytic signal magnitude envelope (like in original code)
    x = np.sqrt(np.abs(hilbert(y)) ** 2)
    x = x - np.mean(x)

    # Frequency-domain complex exponential terms
    w = np.exp(-1j * 2 * np.pi * (f2 - f1) / (k * fs))
    a = np.exp(1j * 2 * np.pi * f1 / fs)

    # Prepare chirp modulation vectors
    kk = np.arange(-m + 1, max(k - 1, m - 1) + 1)
    kk=kk.reshape(-1, 1)
    kk2 = (kk ** 2) / 2
    ww = w ** kk2

    nn = np.arange(0, m).reshape(-1, 1)
    aa = a ** (-nn)
    aa = aa * ww[(m + nn - 1).astype(int)]  # Adjust for 0-indexing
    y_mod = x * aa

    # Linear chirp filtering using FFT
    nfft = 2 ** nextpow2(m+k-1)
    fy = fft(y_mod, nfft,axis=0)
    fv = fft(1 / ww[:(k - 1 + m)], nfft,axis=0)
    fv=fv.reshape(-1, 1)
    fy_filtered = fy * fv

    g_full = ifft(fy_filtered,axis=0)

    # Post-processing
    g = g_full[m - 1: m + k - 1] * (ww[m - 1: m + k - 1].reshape(-1, 1))

    return g


def get_caf(data,alpha,tau):
    return np.mean(data*np.conj(np.roll(data,tau))*np.exp(-2j*np.pi*alpha*np.arange(data.shape[0])))

def get_cfsd_optimized(data, alphas, taus):
    """
    The cross-correlation can be efficiently computed using the Fast Fourier Transform (FFT) and the Inverse Fast Fourier Transform (IFFT).
    Refer to:
    https://phys.uri.edu/nigh/NumRec/bookfpdf/f13-2.pdf
    """
    n = data.shape[0]
    data_conj = np.conj(data)
    # Precompute FFT of conjugated data once
    fft_data_conj = np.fft.fft(data_conj)

    # Convert taus to indices for array slicing
    # Ensure all tau values map to valid indices in data array
    indices = taus % n
    CFSD = np.zeros(len(alphas), dtype=float)
    for j, alpha in enumerate(alphas):
        # Compute exponential term and modulated signal
        exp_term = np.exp(-2j * np.pi * alpha * np.arange(n))
        y = data * exp_term
        # Compute cross-correlation via FFT for all possible shifts
        fft_y = np.fft.fft(y)
        cross_corr = np.fft.ifft(fft_y * np.conj(fft_data_conj)) / n
        # Extract relevant taus and compute spectral density
        CAF = cross_corr[indices]
        csd = np.fft.fft(CAF)
        CFSD[j] = np.sum(np.abs(csd))
    return CFSD



def degree_peak(cfsd):
    return np.max(cfsd)/np.median(cfsd)