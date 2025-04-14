import sys
import subprocess
import numpy as np
from matplotlib import pyplot as plt
from load_data import load_wav,pre_process
from noise_detect_phase_1 import noise_detection_phase_1
from hr_estimate import pre_find_hr

def plot_signal(data,title):
    plt.plot(np.linspace(0, len(data)/samplerate, len(data)), data)
    plt.title(title)
    plt.show()
    return
def down_sampling(data, samplerate, target_fre):
    factor = int(samplerate / target_fre)
    return int(samplerate / factor), data[::factor]



patient_id=sys.argv[1]
pos=sys.argv[2]
data_path='./data/physionet_data/test_data/'+patient_id+'/'+patient_id+'_'+pos+'.wav'
#data_path='./test_clean_pcg.wav'
samplerate, data = load_wav(data_path)
target_fre=2000
samplerate,data=down_sampling(data,samplerate,target_fre)
data= pre_process(data)
plot_signal(data,'Original Signal')

# estimate hear cycle first
est_hr=pre_find_hr(data,samplerate)


# start phase 1

start = 0
end = start+4
ref_seg=[]

while end <= len(data)/samplerate:
    result=noise_detection_phase_1(patient_id,pos,start,end,est_hr)
    if result is not False:
        ref_seg.append(result)
    start=start+1
    end=end+1

if not ref_seg:
    print(f"fPatient id {patient_id} position {pos} Noisy signal")
else:
    ref=ref_seg[0]
    plot_signal(ref,'Ref Signal')

    from noise_detect_phase_2 import *
    ref_te=ref_max_te(ref, samplerate)
    for i in range(0,len(data)-len(ref),int(0.5*samplerate)):
        test=data[i:int(i+len(ref))]
        # first criteria
        srms_evaluate(ref,test,samplerate)
        # second criteria
        rte=test_rte(test,samplerate,ref_te)
        te_evaluate(rte)


