from dataclasses import dataclass, field, replace
import matplotlib.pyplot as plt
from .contourplotter import ContourPlotter
import pandas as pd


@dataclass
class ContourValidationPlotter:
    contour_plotter: ContourPlotter
    num_data: pd.DataFrame = field(default=None)
    exp_data: pd.DataFrame = field(default=None)

    def __post_init__(self):
        self.num_plotter = replace(self.contour_plotter,
                                   )
        self.num_plotter.update_dataset(self.num_data)
        self.exp_plotter = replace(self.contour_plotter,
                                   )
        self.exp_plotter.update_dataset(self.exp_data)

    def plot(self, ax=None):
        data_attr = (self.num_data, self.exp_data)
        no_data = any(data is None for data in data_attr)
        if no_data:
            raise ValueError("No data given yet!")
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(15, 12))

        ax, _, exp_contours, _ = self.exp_plotter.plot(ax)
        self.num_plotter.levels = exp_contours.levels
        ax, _, num_contours, _ = self.num_plotter.plot(ax)

        x_col = self.contour_plotter.x_col
        y_col = self.contour_plotter.y_col
        x_min = min(data[x_col].min() for data in data_attr)
        x_max = max(data[x_col].max() for data in data_attr)
        ax.set_xlim(x_min, x_max)
        y_min = min(data[y_col].min() for data in data_attr)
        y_max = max(data[y_col].max() for data in data_attr)
        ax.set_ylim(y_min, y_max)
        plt.colorbar(exp_contours, ax=ax)
        ax.axvline(0, ls="--", color="k")
        return ax, num_contours, exp_contours

    def set_numerical_cmap(self, cmap, norm=None):
        self.num_plotter.set_cmap(cmap, norm)

    def set_experimental_cmap(self, cmap, norm=None):
        self.exp_plotter.set_cmap(cmap, norm)

    def set_equal_cmaps(self, cmap, norm=None):
        self.set_numerical_cmap(cmap, norm)
        self.set_experimental_cmap(cmap, norm)

    def update_contour_column(self, new_contour_col):
        self.num_plotter.set_contour_column(new_contour_col)
        self.exp_plotter.set_contour_column(new_contour_col)

    def update_contourf_args(self, **new_args):
        self.num_plotter.update_contourf_args(**new_args)
        self.exp_plotter.update_contourf_args(**new_args)



