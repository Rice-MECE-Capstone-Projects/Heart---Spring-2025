import numpy as np
from scipy.signal import butter, filtfilt
from scipy.signal import decimate


def down_sample(signal,fs):
        target_fs = 1000
        decimation_factor = int(fs / target_fs)

        if fs % target_fs != 0:
            raise ValueError("Original sampling rate must be an integer multiple of 1000 Hz.")
        # Use decimate with FIR filter for better quality (zero-phase by default)
        downsampled_signal = decimate(signal, decimation_factor, ftype='fir', zero_phase=True)
        return downsampled_signal

def pre_processing(input_signal,fs):
    #input_signal = down_sample(input_signal,fs)
    input_signal =input_signal/np.std(input_signal)
    dspike_signal = remove_spike(input_signal)
    # High-pass filter to remove baseline wandering
    fc = 2  # Cut-off frequency (Hz)
    b, a = butter(N=3, Wn=2 * fc / fs, btype='highpass')
    dwander = filtfilt(b, a, dspike_signal)
    # Normalize the signal to standard deviation
    output_signal = dwander / np.std(dwander)
    return output_signal


def remove_spike(input_signal):
    R = 3
    dspike_signal = np.copy(input_signal)

    abs_signal = np.abs(input_signal)
    sort_abs = np.sort(abs_signal)[::-1]  # Descending sort

    # Threshold: average of top 10% absolute values
    TH = np.mean(sort_abs[:int(len(input_signal) * 0.1)])

    # Indices of spikes
    ind_spike = np.where(abs_signal > R * TH)[0]

    if ind_spike.size > 0:
        L_one_percent = int(round(len(input_signal) * 0.01))
        if len(ind_spike) > L_one_percent:
            # Sort found spikes by amplitude descending
            ampi = np.argsort(abs_signal[ind_spike])[::-1]
            selected_indices = ind_spike[ampi[:L_one_percent]]
            dspike_signal[selected_indices] = np.sign(input_signal[selected_indices]) * R * TH

        # Apply replacement to all found spikes (including re-applying to the top 1%)
        dspike_signal[ind_spike] = np.sign(input_signal[ind_spike]) * R * TH

    return dspike_signal



