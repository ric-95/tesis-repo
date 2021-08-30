from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from matplotlib import axes
from ._factories import default_ax_factory
from matplotlib import markers as _markers

FILLED_MARKERS = ("o",
                  "X",
                  "v",
                  "^",
                  "<",
                  ">")
UNFILLED_MARKERS = (".",
                    "x",
                    _markers.CARETDOWN,
                    _markers.CARETUP,
                    _markers.CARETLEFT,
                    _markers.CARETRIGHT)
_LOOSELY_DASHDOTDOTTED = (0, (3, 10, 1, 10, 1, 10))
_DASHDOTDOTTED = (0, (3, 5, 1, 5, 1, 5))
_DENSELY_DASHED = (0, (5, 1))
_LOOSELY_DASHED = (0, (5, 10))
DEFAULT_LINESTYLES = ("solid",
                      "dashed",
                      "dashdot",
                      _DASHDOTDOTTED,
                      _DENSELY_DASHED,
                      _LOOSELY_DASHED,)
DEFAULT_COLORS = ("tab:blue",
                  "tab:orange",
                  "tab:green",
                  "tab:red",
                  "tab:purple",
                  "tab:olive",
                  "tab:brown",
                  "tab:cyan",
                  "indianred",
                  "goldenrod",
                  "darkseagreen",
                  "firebrick",
                  "teal",
                  "sienna",
                  )
DEFAULT_MARKERS = UNFILLED_MARKERS


@dataclass
class Plotter(ABC):

    @abstractmethod
    def plot(self, ax: axes.Axes):
        raise NotImplementedError

    @staticmethod
    def _ax_factory(ax=None, **kwargs):
        if ax is None:
            _, ax = plt.subplots(1, 1, **kwargs)
            return ax
        return ax
