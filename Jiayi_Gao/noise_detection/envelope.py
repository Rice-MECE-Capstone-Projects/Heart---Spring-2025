from scipy.signal import lfilter
import numpy as np
from scipy.signal import correlate

def divide_freq_space(freq_low, freq_high, n_band,
                      divide_type='ERB'):
    if divide_type == 'ERB':
        if n_band == 1:
            return np.asarray(freq_low, dtype=float).reshape(1, )
        print(freq_low)
        low_erb = Hz2ERBscal(freq_low)
        high_erb = Hz2ERBscal(freq_high)
        erb_elem = (high_erb - low_erb) / (n_band - 1)
        f = ERBscal2Hz(low_erb + erb_elem * np.arange(n_band))
    else:
        raise Exception('unsupport Divide type')
    return f
def Hz2ERBscal(freq):
    """convert Hz to ERB scale"""
    return 21.4 * np.log10(4.37 * freq / 1e3 + 1)


def ERBscal2Hz(erb_num):
    """convert ERB scale to Hz"""
    return (10 ** (erb_num / 21.4) - 1) / 4.37 * 1e3


def cal_ERB(cf):
    return 24.7 * (4.37 * cf / 1000 + 1.0)


def cal_bw(cf):
    erb = cal_ERB(cf)
    return 1.019 * erb
def filter(T,input,freq_low,freq_high):
    cf=divide_freq_space(freq_low, freq_high, 1)
    n = np.arange(len(input))
    shiftor = np.exp(1j * 2 * np.pi * cf * n *T)
    input_prime=input * shiftor
    b=float(cal_bw(cf)[0])
    k=np.exp(-2*np.pi*b*T)
    numerator = np.array([0, 1, 4*k, k**2],dtype=complex)
    denominator = np.array([1, -4*k, 6*k**2, -4*k**3, k**4],dtype=complex)
    numerator = np.array([T**3 * coef for coef in numerator],dtype=complex)
    output_prime= lfilter(numerator, denominator, input_prime)
    output=np.real(output_prime/shiftor)
    return output
def normalized_correlation(x, w):
    numerator = correlate(x * w, x * w, mode="full")
    denominator = correlate(w , w , mode="full")
    denominator[denominator == 0] = 1e-5
    return numerator / denominator

def normalize_envelope(signal):
    median=np.median(signal)
    max_value=np.max(np.abs(signal))
    normalized_signal=np.zeros_like(signal)
    for i in range(len(signal)):
        normalized_signal[i]=(signal[i]-median)/max_value
    return normalized_signal