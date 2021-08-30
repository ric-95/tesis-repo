import matplotlib.axes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import lines as _lines
import seaborn as sns
from collections import namedtuple
from typing import Union, Sequence, Any
from ._numericalvalidation1dplotter import NumericalValidation1DPlotter
from ._defaults import DEFAULT_COLORS, DEFAULT_LINESTYLES, DEFAULT_MARKERS


def plot1d_numerical_validation(numerical_x: np.ndarray,
                                numerical_y: np.ndarray,
                                experimental_x: np.ndarray = None,
                                experimental_y:  np.ndarray = None,
                                numerical_labels: Sequence[str] = None,
                                experimental_labels: Sequence[str] = None,
                                linestyles: Sequence[str] = None,
                                markers: Any = None,
                                numerical_colors=None,
                                experimental_colors=None,
                                ax: matplotlib.axes.Axes = None,
                                title: str = "",
                                ):
    total_numerical_series = numerical_y.shape[1]
    if experimental_y is None:
        total_experimental_series = len(DEFAULT_COLORS)
    else:
        total_experimental_series = experimental_y.shape[1]
    if numerical_colors is None:
        numerical_colors = list(DEFAULT_COLORS[:total_numerical_series])
    if experimental_colors is None:
        experimental_colors = DEFAULT_COLORS[:total_experimental_series]

    plotter = NumericalValidation1DPlotter(
        num_x=numerical_x,
        num_y=numerical_y,
        num_colors=numerical_colors,
        num_labels=numerical_labels,
        exp_x=experimental_x,
        exp_y=experimental_y,
        exp_labels=experimental_labels,
        exp_colors=experimental_colors,
        linestyles=linestyles,
        markers=markers,
        title=title,
    )
    return plotter.plot(ax)


def plot_marker_only(ax, x, y, marker, **kwargs):
    ax.plot(x, y, marker=marker, linestyle=None, **kwargs)


def plot_2d_flow_contour(data, x, y, field, ax=None, **kwargs):
    """Plots a 2D flow contour.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe containing flow data
    x : str
        Key for the x coordinate
    y : str
        Key for the y coordinate
    field : str
        Key for field to plot
    ax : matplotlib.axes.Axes
        Axis to plot contour to. If None a new figure with axes ar
    kwargs
        Keyword arguments to pass to plotting method.
    """
    pivot = data.pivot(index=y, columns=x, values=field)
    xx, yy = np.meshgrid(pivot.columns.to_numpy(), pivot.index.to_numpy())
    field = pivot.to_numpy()
    if ax is None:
        _, ax = plt.subplots(1, 1)
    ax.imshow(field, **kwargs)


def _default_handler(linestyles=None,
                     linecolors=None,
                     markers=None,
                     markercolors=None,
                     ):
    if linestyles is None:
        linestyles = DEFAULT_LINESTYLES
    if linecolors is None:
        linecolors = DEFAULT_COLORS
    if markers is None:
        markers = DEFAULT_MARKERS
    if markercolors is None:
        markercolors = DEFAULT_COLORS
    return linestyles, linecolors, markers, markercolors


def _init_colors(colors=None):
    if colors is None:
        return DEFAULT_COLORS
    return colors
