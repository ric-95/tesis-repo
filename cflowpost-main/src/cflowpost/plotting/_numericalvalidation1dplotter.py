import matplotlib.axes as axes
from matplotlib.font_manager import FontProperties
from ._baseplotter import Plotter
from dataclasses import dataclass, field
import numpy as _np
from typing import Sequence, Any
from ._gridformatter import GridFormatter
from ._factories import dashed_minor_grid_factory as dashed_minor_grid
from ._factories import cyclical_factory
from ._defaults import DEFAULT_MARKERS, DEFAULT_COLORS, DEFAULT_LINESTYLES
from typing import Union


def _array_factory():
    return _np.full(shape=(1,), fill_value=_np.nan)


@dataclass
class NumericalValidation1DPlotter(Plotter):
    num_x: _np.ndarray
    num_y: _np.ndarray
    num_colors: Sequence[str] = field(default=DEFAULT_COLORS)
    exp_x: Union[_np.ndarray, None] = field(default=None)
    exp_y: Union[_np.ndarray, None] = field(default_factory=_array_factory)
    exp_colors: Sequence[str] = field(default=DEFAULT_COLORS)
    num_labels: Sequence[str] = field(default=None)
    exp_labels: Sequence[str] = field(default=None)
    linestyles: Sequence[str] = field(default=DEFAULT_LINESTYLES)
    markers: Sequence[Any] = field(default=DEFAULT_MARKERS)
    grid_formatter: GridFormatter = field(default_factory=dashed_minor_grid)
    title: str = ""
    title_fontproperties: FontProperties = field(default=None)
    legend: bool = True
    markersize: float = 3
    base_fontsize: float = 10
    markevery: float = None

    def __post_init__(self):

        if self.exp_y is None:
            self.exp_y = _array_factory()

        if self.num_y.ndim > 2:
            raise ValueError("This array is too big! Maximum of 2 dimensions"
                             f"at a time. {self.num_y.ndim} dimensions given.")
        if self.exp_y.ndim > 2:
            raise ValueError("This array is too big! Maximum of 2 dimensions"
                             f"at a time. {self.exp_y.ndim} dimensions given.")
        if self.markers is None:
            self.markers = DEFAULT_MARKERS
        if self.num_colors is None:
            self.num_colors = DEFAULT_COLORS
        if self.linestyles is None:
            self.linestyles = DEFAULT_LINESTYLES
        try:
            num_sets = self.num_y.shape[1]
        except IndexError:
            num_sets = 1
        try:
            exp_sets = self.exp_y.shape[1]
        except IndexError:
            exp_sets = 1
        self.markers = cyclical_factory(self.markers, exp_sets)
        self.num_colors = cyclical_factory(self.num_colors, num_sets)
        self.exp_colors = cyclical_factory(self.exp_colors, exp_sets)
        self.linestyles = cyclical_factory(self.linestyles, num_sets)

    def plot(self, ax: axes.Axes = None, ):
        ax = self._ax_factory(ax)
        numeric_lines = ax.plot(self.num_x,
                                self.num_y,
                                label=self.num_labels,)
        for line, color, linestyle in zip(numeric_lines,
                                          self.num_colors,
                                          self.linestyles):
            line.set_color(color)
            line.set_linestyle(linestyle)

        if self.exp_x is not None:
            exp_markers = ax.plot(self.exp_x,
                                  self.exp_y,
                                  label=self.exp_labels,
                                  markersize=self.markersize)
            for marker, color, markerstyle in zip(exp_markers,
                                                  self.exp_colors,
                                                  self.markers):
                marker.set_color(color)
                marker.set_marker(markerstyle)
                marker.set_linestyle("None")
                marker.set_markerfacecolor("None")
                marker.set_markevery(self.markevery)

        self.grid_formatter.format(ax)
        if self.title:
            ax.set_title(self.title,
                         fontproperties=self.title_fontproperties,)
        if self.legend:
            ax.legend()
        return ax

    def change_numerical_data(self, num_x=None, num_y=None):
        if num_x is not None:
            self.num_x = num_x
        if num_y is not None:
            self.num_y = num_y
        return self

    def change_experimental_data(self, exp_x=None, exp_y=None):
        if exp_x is not None:
            self.exp_x = exp_x
        if exp_y is not None:
            self.exp_y = exp_y
        return None

    def remove_experimental_data(self):
        self.exp_x = None
        self.exp_y = None
