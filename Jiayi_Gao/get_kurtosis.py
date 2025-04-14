import numpy as np
# feature 1

def get_kurtosis(x):
    """
    Calculates the kurtosis of input signal x (zero-mean).
    Equivalent to: kurtosis = E[x^4] / (E[x^2]^2 + eps)
    """
    x = x - np.mean(x)

    k1 = np.sum(x ** 4) / len(x)
    k2 = np.sum(x ** 2) / len(x)

    # Use machine epsilon to avoid division by zero
    kur = k1 / (k2 ** 2 + np.finfo(float).eps)

    return kur