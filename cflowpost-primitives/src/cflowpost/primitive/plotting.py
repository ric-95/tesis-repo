import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_2d_flow_contour(data, x, y, field, ax=None):
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
    """
    pivot = data.pivot(index=y, columns=x, values=field)
    xx, yy = np.meshgrid(pivot.columns.to_numpy(), pivot.index.to_numpy())
    field = pivot.to_numpy()
