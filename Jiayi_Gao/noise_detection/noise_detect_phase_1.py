import matplotlib.pyplot as plt
import numpy as np
from load_data import load_wav,pre_process,down_sample
from scipy.signal import hilbert
from envelope import filter, normalized_correlation, normalize_envelope
from hr_estimate import find_hr_SVD, find_hr_single_peak
from find_peak import find_promin_peaks
from criteria_1 import check_criteria_1
from time_frequency_autocor import fre_bands_spectrum, get_auto_cor_bands
from criteria_2 import check_criteria_2
from criteria_3 import check_criteria_3

def noise_detection_phase_1(patient_id,patient_pos,start,end,est_hr):
    def plot_signal(data, title):
        plt.plot(np.linspace(0, len(data) / samplerate, len(data)), data)
        plt.title(title)
        plt.show()
        return

    # load data
    data_path='./data/physionet_data/test_data/'+patient_id+'/'+patient_id+'_'+patient_pos+'.wav'
    #data_path = './data/New_N_001.wav'
    #data_path = './test_clean_pcg.wav'
    target_fre=2000
    samplerate, data = load_wav(data_path)
    data= down_sample(data,samplerate)
    samplerate=2000
    data= pre_process(data)
    data_time_eva=data[int(start*samplerate):int(end*samplerate)]

    # Phase 1

    # extract envelop of HS components by Hilbert transform and Gammatone band-pass filter and auto correlation
    envelope=np.abs(hilbert(data_time_eva))
    envelope=np.abs(filter(T=1/samplerate,input=envelope,freq_low=0,freq_high=target_fre/2))
    envelope=normalize_envelope(envelope)
    #plot_signal(envelope,'envelope of heart signal')
    win=np.hanning(envelope.shape[0])
    corr=normalized_correlation(envelope,win)
    corr=corr[0:int(len(corr)/2)]
    #plot_signal(corr,'auto correlation of heart signal envelope')


    # select the prominent peaks
    # use estimated heart rate from previous step
    promin_peaks=find_promin_peaks(corr,samplerate,est_hr)
    #print([int(x)/samplerate for x in promin_peaks])
    peak_indice=np.sort([int(x) for x in promin_peaks])

    # plot peaks
    plt.plot(np.linspace(0, len(corr)/samplerate, len(corr)), corr)
    plt.title("auto correlation of envelop with peaks")
    plt.scatter(np.linspace(0, len(data)/samplerate, len(data))[peak_indice], corr[peak_indice], color='red', s=50, label="Highlighted Points", zorder=3)
    plt.show()
    #print([corr[p] for p in peak_indice])

    # check criteria 1
    c1=check_criteria_1(peak_indice,corr,samplerate)
    if not c1:
        return False




    # Periodicity in time-frequency domain

    # STFT for the signal(with window function) and divide into 15 frequency bands in 0-600Hz and calculate spectral energy
    fre_bands=fre_bands_spectrum(data_time_eva, samplerate)

    # auto correlation of each frequency band
    as_k=get_auto_cor_bands(fre_bands)
    fig, axes = plt.subplots(15, 1, figsize=(15, 10), sharex=True)

    for i in range(15):

        axes[i].plot(np.linspace(0,as_k.shape[1]/samplerate,fre_bands.shape[1]),as_k[i], label=f"Row {i+1}")
        plt.xlim(0,as_k.shape[1]/samplerate)
    axes[-1].set_xlabel("Time (s)")
    axes[-1].set_ylabel("Frequency (Hz)")
    plt.show()

    # check criteria 2 monotonicity
    c2=check_criteria_2(as_k)
    if not c2:
        return False



    ## check criteria 3 peak alignment
    c3=check_criteria_3(as_k,est_hr,samplerate)
    if not c3:
        return False


    return data_time_eva

