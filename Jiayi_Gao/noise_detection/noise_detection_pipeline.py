import sys
import subprocess
import numpy as np
from matplotlib import pyplot as plt
from load_data import load_wav,pre_process
from noise_detect_phase_1 import noise_detection_phase_1

def plot_signal(data,title):
    plt.plot(np.linspace(0, len(data)/samplerate, len(data)), data)
    plt.title(title)
    plt.show()
    return



patient_id=sys.argv[1]
pos=sys.argv[2]
data_path='./data/'+patient_id+'/'+patient_id+'_'+pos+'.wav'
#data_path='./data/New_N_001.wav'
samplerate, data = load_wav(data_path)
#data=np.hstack((data, data))
plot_signal(data,'Original Signal')

start = 0
end = start+4
ref_seg=[]

while end <= len(data)/samplerate:
    result=noise_detection_phase_1(patient_id,pos,start,end)
    if result:
        ref_seg.append(start)
    start=start+0.5
    end=end+0.5

print(ref_seg)
