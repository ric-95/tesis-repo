from scipy import signal as _signal
import matplotlib.pyplot as _plt
import numpy as _np


def compute_welch_psd(time_series, sampling_rate, **kwargs):
    return _signal.welch(time_series, sampling_rate, **kwargs)


def plot_periodogram(f, pxx, y_min, y_max, ax=None):
    if ax is None:
        fig, ax = _plt.subplots(1, 1)
    ax.loglog(f, _np.sqrt(pxx))
    ax.set_ylim(y_min, y_max)
    ax.grid("both")
    return ax
