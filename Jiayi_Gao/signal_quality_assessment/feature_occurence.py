import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd

dataset=np.load('dataset_bin.npz')

label=dataset['target'].reshape(-1,1)
data=dataset['data']

feature_names = ['Kurosis(signal)', 'Energy ratio(Low)', 'Energy ratio(Mid)', 'Energy ratio(High)', 'Std(envelope)', 'Sample Entropy(envelope)', 'Kurosis(auto correlation)', 'Max Peak(auto correlation)', 'Sample Entropy(auto correlation)', 'Degree of periodicity']
# plot
colors = {
    0: '#4B4EA2',  # Unacceptable (blueish)
    1: '#E44B4B'   # Acceptable (reddish)
}
label = label.ravel()


fig, axes = plt.subplots(2, 5, figsize=(20, 10))
axes = axes.flatten()

for i in range(10):
    ax = axes[i]
    for lbl in [1, 0]:  # red first, blue on top
        values = data[label == lbl, i]
        counts, bins = np.histogram(values, bins=100,density=False)


        # Normalize counts to be within [0, 1]
        counts = counts / values.shape[0]

        # Compute bin centers for bar positioning
        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        width = bins[1] - bins[0]

        ax.bar(
            bin_centers,
            counts,
            width=width,
            alpha=0.8,
            color=colors[lbl],
            label='Acceptable' if lbl == 1 else 'Unacceptable'
        )

    ax.set_title(f'Feature No. {i + 1}')
    ax.set_xlabel(feature_names[i])
    ax.set_ylim(0, ax.get_ylim()[1]*1.1)  # All y-axes normalized to 1

    if i == 9:
        ax.legend(loc='upper right')

plt.tight_layout()
plt.show()