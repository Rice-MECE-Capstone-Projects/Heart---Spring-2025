import numpy as np

from find_peak import find_promin_peaks


def check_criteria_3(as_k,est_heart_cycle,fs):
    num_of_peaks = int(as_k.shape[1] / fs / est_heart_cycle)
    peaks_in_fre_bands = np.zeros((15, num_of_peaks))
    for i in range(15):
        peaks_in_fre_bands[i] = find_promin_peaks(as_k[i][:as_k.shape[1]], fs, est_heart_cycle)
    num_of_aligned_peaks = 0
    for j in range(num_of_peaks):
        flag = 0
        standard = peaks_in_fre_bands[0][j]
        low_limit = standard * 0.9
        high_limit = standard * 1.1
        for k in range(1, 15):
            if peaks_in_fre_bands[k][j] < low_limit or peaks_in_fre_bands[k][j] > high_limit:
                flag = 1
                break
        if flag == 0:
            num_of_aligned_peaks = num_of_aligned_peaks + 1
    #print(num_of_aligned_peaks)
    if num_of_aligned_peaks == num_of_peaks:
        print("Passed criteria 3")
        return True
    print("Failed criteria 3")
    return  False