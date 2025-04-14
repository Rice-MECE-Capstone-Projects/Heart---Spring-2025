#!/usr/bin/env python
# coding: utf-8
import math
import time

from scipy.signal import resample_poly

from get_autocorr_envelop import *
from pre_processing import *
from get_quality_index import *
import importlib
from scipy.io import wavfile
data_path='./data/13596_AV.wav'
def load_wav(wav_path):
    sample_rate, data = wavfile.read(wav_path)
    return sample_rate, data

ori_fs,ori_data=load_wav(data_path)


# In[5]:
def get_feature(ori_data, ori_fs):
    #start=time.time()
    data=pre_processing(ori_data, ori_fs)
    fs=1000
    # feature 1
    from get_kurtosis import get_kurtosis
    feature_1=get_kurtosis(data)
    # feature 2,3,4
    from get_energy_ratio import get_energy_ratio
    fre_Low=[24,144]
    fre_High=[200,500]
    fre_Mid=[144,200]
    feature_2=get_energy_ratio(data,fre_Low,fs)
    feature_3=get_energy_ratio(data,fre_Mid,fs)
    feature_4=get_energy_ratio(data,fre_High,fs)
    #print("first 5 features:",time.time()-start)
    # feature 5,6
    from get_envelope_std_entropy import get_envelope_from_stft,get_envelop_sample_entropy
    envelope=get_envelope_from_stft(data,fs)
    feature_5=np.std(envelope)/1000
    # need down sample
    fsd=40
    gcd_val=math.gcd(fsd,fs)
    up=fsd//gcd_val
    down=fs//gcd_val
    down_enve=resample_poly(envelope,up,down)
    feature_6=get_envelop_sample_entropy(down_enve/np.std(down_enve),2,0.2)
    # feature 7,8,9
    auto_corr_enve=get_autocorr_envelop(envelope)
    feature_7=get_kurtosis(auto_corr_enve)
    feature_8=get_max_autocorr_coeff(auto_corr_enve,fs)
    down_enve_auto_corr=resample_poly(auto_corr_enve,up,down)
    feature_9=get_envelop_sample_entropy(down_enve_auto_corr/np.std(down_enve_auto_corr),2,0.2)
    #print("first 9 features:", time.time() - start)
    # feature 10
    min_cf=0.3
    max_cf=2.5
    alphas=np.arange(min_cf,max_cf,0.1)
    taus=np.arange(-1000,1000)
    cfsd=get_cfsd_optimized(data,alphas,taus)
    feature_10=degree_peak(cfsd)
    #print("end", time.time() - start)
    return np.array([feature_1,feature_2,feature_3,feature_4,feature_5,feature_6,feature_7,feature_8,feature_9,feature_10])

