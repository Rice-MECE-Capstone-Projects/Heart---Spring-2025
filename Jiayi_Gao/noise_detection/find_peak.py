import numpy as np
from scipy.signal import find_peaks


def find_promin_peaks(signal,fs,est_heart_cycle):

    window_size=int(fs*est_heart_cycle)
    num_heart_cycles = (int(np.floor(len(signal) /window_size)))


    # trim start and end
    peaks,property=find_peaks(signal)
    for peak in peaks:
        if peak<window_size or peak >len(signal) - int(0.1 * fs):
            peaks=np.delete(peaks,np.where(peaks==peak))
    #print(peaks)
    if len(peaks)==0:
        return []
    highest_peak = peaks[np.argmax(signal[peaks])]

    selected_peaks = [highest_peak]


    def find_adjacent_peak(reference_peak, direction):
        if direction == -1:
            window_start, window_end = max(0, reference_peak - window_size), reference_peak
        else:
            window_start, window_end = reference_peak, min(len(signal), reference_peak + window_size)

        candidates = [p for p in peaks if (window_start < p < window_end) and (np.abs(p-reference_peak)>window_size/2)]
        if candidates:
            return max(candidates, key=lambda p: signal[p])
        return None


    for peak in selected_peaks:
        left_peak = find_adjacent_peak(peak, -1)
        #print(left_peak)
        if left_peak and left_peak not in selected_peaks and signal[left_peak] > np.mean(signal[selected_peaks])/3:
            selected_peaks.append(left_peak)
            if len(selected_peaks) >= num_heart_cycles:
                break
        right_peak = find_adjacent_peak(peak, 1)

        if right_peak and right_peak not in selected_peaks and signal[right_peak] > np.mean(signal[selected_peaks])/3:
            selected_peaks.append(right_peak)
            if len(selected_peaks) >= num_heart_cycles:
                break
    #print(selected_peaks)
    return selected_peaks