import numpy as np

def avg_power(recording):
  """Calculates average power of a recording
  
  Input: A signal, e.g. PCG recording (np.array or similar)
  Output: power (float)
  """
  return np.mean(recording**2)

def snr_calc(clean, noisy):
  """
  Calculate the SNR of a signal given its clean reference.
  """
  clean_power = avg_power(clean)
  noise_signal = noisy - clean
  noise_power = avg_power(noise_signal)
  return 10*np.log10(clean_power/noise_power)

def rmse(clean,noisy):
  """
  Calculate the root mean squared error between two signals
  """
  return avg_power(clean-noisy)**0.5
