import numpy as np

def check_criteria_1(peaks,signal,fs):
    peaks=np.sort(peaks)
    peak_point=[(i/fs,float(signal[i])) for i in peaks]
    peak_vector=[(peak_point[i][0]-peak_point[i+1][0],peak_point[i][1]-peak_point[i+1][1]) for i in range(len(peak_point)-1)]
    for j in range(len(peak_vector)-1):
        cos=cosine_similarity(peak_vector[j],peak_vector[j+1])
        if abs(cos)<0.8:
            print("Failed criteria 1")
            return False
    print("Passed criteria 1")
    return True


def cosine_similarity(y_r, y_r1):

    inner_product = np.dot(y_r, y_r1)
    norm_y_r = np.linalg.norm(y_r)
    norm_y_r1 = np.linalg.norm(y_r1)

    # Avoid division by zero
    if norm_y_r == 0 or norm_y_r1 == 0:
        return 0  # Or handle as needed

    return inner_product / (norm_y_r * norm_y_r1)