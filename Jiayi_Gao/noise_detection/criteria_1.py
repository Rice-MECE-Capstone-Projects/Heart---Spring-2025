import numpy as np
from scipy.spatial.distance import cosine

def check_criteria_1(peaks,signal,fs):
    peaks=np.sort(peaks)
    peak_point=[(i/fs,float(signal[i])) for i in peaks]
    x_vec= [peak_point[i][0]-peak_point[i+1][0] for i in range(len(peak_point)-1)]

    y_vec = [(peak_point[i][1]-peak_point[i+1][1])/np.max(signal)*4 for i in range(len(peak_point)-1)]

    peak_vector=[[x_vec[i],y_vec[i]] for i in range(len(peak_point)-1)]
    for j in range(len(peak_vector)-1):
        cos=1-cosine(peak_vector[j],peak_vector[j+1])
        if abs(cos)<0.8:
            print("Failed criteria 1")
            return False
    print("Passed criteria 1")
    return True