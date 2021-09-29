from dataclasses import dataclass, field, replace
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


@dataclass
class ContourPlotter:
    x_col: str
    y_col: str
    u_col: str
    v_col: str
    contour_col: str
    levels: int
    streamplot_args: dict = field(default_factory=dict)
    contourf_args: dict = field(default_factory=dict)
    contour_args: dict = field(default_factory=dict)
    data: pd.DataFrame = field(default=None, repr=False)

    def __post_init__(self):
        if self.data is not None:
            self.data = self.update_dataset(self.data, )
        self.contour_args.setdefault("linewidths", 0.5)
        self.contour_args.setdefault("colors", "black")

    def update_dataset(self, new_data,
                       new_x_col=None,
                       new_y_col=None,
                       already_pivoted=False):
        if already_pivoted:
            self.data = new_data
            return

        if new_x_col is not None:
            self.x_col = new_x_col
        if new_y_col is not None:
            self.y_col = new_y_col
        self.data = self._pivot_data(new_data)
        return

    def plot(self, ax=None):
        if self.data is None:
            raise ValueError("No data has been given yet!")
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(15, 12))
        pivot = self.data
        u, v = pivot[self.u_col], pivot[self.v_col]
        corrected_x = self._resample_uniform_series(u.columns)
        corrected_y = self._resample_uniform_series(u.index)
        extent = (corrected_x.min(), corrected_x.max(), corrected_y.min(),
                  corrected_y.max())
        field = pivot[self.contour_col]
        streamlines = ax.streamplot(x=corrected_x,
                                    y=corrected_y,
                                    u=u, v=v,
                                    **self.streamplot_args)
        contours = ax.contourf(corrected_x,
                               corrected_y,
                               field,
                               self.levels, **self.contourf_args)
        contour_lines = ax.contour(corrected_x, corrected_y, field,
                                   levels=contours.levels, **self.contour_args)
        return ax, streamlines, contours, contour_lines

    @staticmethod
    def _pìvot_to_2d(data, x_col, y_col):
        return data.pivot(y_col, x_col)

    def _pivot_data(self, data):
        return self._pìvot_to_2d(data, self.x_col, self.y_col)

    @staticmethod
    def _resample_uniform_series(series):
        return np.linspace(series.min(), series.max(), len(series))

    def set_cmap(self, cmap, norm=None):
        self.contourf_args["cmap"] = cmap
        if norm is not None:
            self.contourf_args["norm"] = norm
        return

    def set_contour_column(self, new_contour_col):
        # TODO: Add check if the given value is in dataset. Careful
        # with the multiindex!
        #         if new_contour_col not in self.data.columns:
        #             raise KeyError("Given key missing from dataset columns.")
        self.contour_col = new_contour_col

    def update_contourf_args(self, **new_args):
        self.contourf_args.update(new_args)
