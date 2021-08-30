import matplotlib.pyplot as plt
from ._gridformatter import GridFormatter
from matplotlib.font_manager import FontProperties
from itertools import cycle, islice


def default_ax_factory():
    _, ax = plt.subplots(1, 1)
    return ax


def dashed_minor_grid_factory():
    return GridFormatter.dashed_minor()


def modern_fontproperties():
    return FontProperties(family="sans-serif", )


def cyclical_factory(seq_to_cycle, n):
    return list(islice(cycle(seq_to_cycle), n))
