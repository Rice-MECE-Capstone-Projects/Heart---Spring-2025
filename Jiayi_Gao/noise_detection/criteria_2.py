import numpy as np
from hr_estimate import SVD_eva


def check_criteria_2(as_k):
    sg_1 = np.zeros((5, as_k.shape[1]))
    sg_6 = np.zeros((5, as_k.shape[1]))
    sg_11 = np.zeros((5, as_k.shape[1]))
    for i in range(15):
        if i <= 4:
            sg_1[i] = as_k[i]
        elif i <= 9:
            sg_6[i - 5] = as_k[i]
        else:
            sg_11[i - 10] = as_k[i]
    phi_sg = [SVD_eva(sg_1), SVD_eva(sg_6), SVD_eva(sg_11)]
    #print([float(x) for x in phi_sg])
    if phi_sg[0]>phi_sg[1]>phi_sg[2] or phi_sg[0]<phi_sg[1]<phi_sg[2] :
        print("Passed criteria 2")
        return True
    print("Failed criteria 2")
    return False