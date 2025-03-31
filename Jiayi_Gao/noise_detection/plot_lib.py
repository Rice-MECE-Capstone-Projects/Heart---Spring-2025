import numpy as np
import matplotlib.pyplot as plt


def plot_signal(data,title,samplerate):
    plt.plot(np.linspace(0, len(data)/samplerate, len(data)), data)
    plt.title(title)
    plt.show()
    return