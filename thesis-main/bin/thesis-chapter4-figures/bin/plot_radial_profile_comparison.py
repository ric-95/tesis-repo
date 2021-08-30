from argparse import ArgumentParser
from dataclasses import dataclass, field
from typing import Sequence, Mapping, Union, ClassVar
import json
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import cflowpost.plotting as cfplot


CONFIG_DIR = "config"
PLOT_FORMAT_JSON = "plot_format.json"
POSITIONS_JSON = "positions.json"
VARIABLES_JSON = "variables.json"


@dataclass
class CaseComparisonPlotter:
    case_dir: str
    plot_format: OrderedDict
    positions: OrderedDict[str, str]
    variables: OrderedDict
    basewidth: float = field(default=2., repr=False)
    baseheight: float = field(default=2.2, repr=False)
    sharex: Union[str, bool] = field(default="col", repr=False)
    sharey: str = field(default="row", repr=False)
    tight_layout: bool = field(default=True, repr=False)
    base_fontsize: float = field(default=10, repr=False)
    _model_color_key: ClassVar[str] = "Model colors"
    _experimental_color_key: ClassVar[str] = "Experimental color"
    _markevery_key: ClassVar[str] = "markevery"
    _xlim_key: ClassVar[str] = "xlim"
    _xlabel_key: ClassVar[str] = "xlabel"

    def __post_init__(self):
        cls = CaseComparisonPlotter
        self.plot_format.setdefault(
            cls._experimental_color_key, "tab:olive")
        self.plot_format.setdefault(cls._markevery_key, None)
        self.plot_format.setdefault(cls._xlim_key, None)
        self.plot_format.setdefault(cls._xlabel_key, None)

    def create_figure(self):
        nrows, ncols = len(self.variables), len(self.positions)
        figsize = (ncols*self.basewidth, nrows*self.baseheight)
        return plt.subplots(nrows, ncols,
                            figsize=figsize,
                            sharex=self.sharex,
                            sharey=self.sharey,
                            tight_layout=self.tight_layout)

    def read_data(self):
        models = self.plot_format["models"]
        positions = self.positions.keys()
        models = [os.path.join(self.case_dir, model) for model in models]
        experimental = os.path.join(self.case_dir,
                                    self.plot_format["experimental"])
        model_paths_by_position = OrderedDict(
            {position: [os.path.join(model, position) for model in models]
             for position in positions})
        model_data_map = {
            position: [pd.read_csv(path)
                       for path in model_paths_by_position[position]]
            for position in positions}
        exp_data_map = {
            position: pd.read_csv(os.path.join(experimental, position))
            for position in positions}
        return model_data_map, exp_data_map

    def plot(self, ):
        model_data_map, exp_data_map = self.read_data()
        fig, axs = self.create_figure()
        positions = list(self.positions.keys())
        y_variables = list(self.variables.keys())
        model_labels = self.plot_format["models"]
        experimental_label = self.plot_format["experimental"]
        x_var_key = self.plot_format["x_var"]
        xlabel = self.plot_format[self.__class__._xlabel_key]
        xlabel = xlabel if xlabel is not None else x_var_key
        exp_color = self.plot_format[self.__class__._experimental_color_key]
        markevery = self.plot_format[self.__class__._markevery_key]
        xlim = self.plot_format[self.__class__._xlim_key]
        for position, ax in zip(positions, axs[0]):
            ax.set_title(self.positions[position],
                         fontsize=self.base_fontsize*1.5)
        for y_var_key, axs_row in zip(y_variables, axs):
            for position, ax in zip(positions, axs_row):
                model_frames = model_data_map[position]
                experimental_frame = exp_data_map[position]
                self._plot_single_ax(model_frames=model_frames,
                                     experimental_frame=experimental_frame,
                                     x_var_key=x_var_key,
                                     y_var_key=y_var_key,
                                     model_labels=model_labels,
                                     exp_label=experimental_label,
                                     exp_color=[exp_color],
                                     markevery=markevery,
                                     xlim=xlim,
                                     ax=ax)
            axs_row[0].set_ylabel(self.variables[y_var_key],
                                  fontsize=self.base_fontsize * 1.4)
        for ax in axs[-1]:
            ax.set_xlabel(xlabel, fontsize=self.base_fontsize*1.4)
        axs[0][-1].legend()
        fig.align_ylabels()
        return fig, axs

    @staticmethod
    def _plot_single_ax(
            model_frames,
            experimental_frame,
            x_var_key,
            y_var_key,
            model_labels,
            exp_label,
            exp_color,
            markevery,
            xlim=None,
            ax=None,):
        if ax is None:
            fig, ax = plt.subplots(1, 1)
        x_var_series = np.column_stack([data[x_var_key].to_numpy()
                                        for data in model_frames])
        y_var_series = np.column_stack([data[y_var_key].to_numpy()
                                        for data in model_frames])
        x_exp_series = experimental_frame[x_var_key]
        y_exp_series = experimental_frame[y_var_key]
        plotter = cfplot.NumericalValidation1DPlotter(num_x=x_var_series,
                                                      num_y=y_var_series,
                                                      exp_x=x_exp_series,
                                                      exp_y=y_exp_series,
                                                      num_labels=model_labels,
                                                      exp_labels=exp_label,
                                                      exp_colors=exp_color,
                                                      markevery=markevery,
                                                      legend=False)
        plotter.plot(ax=ax)
        if xlim is not None:
            ax.set_xlim(*xlim)
        return


def read_json_as_ordereddict(fileloc):
    with open(fileloc, "r") as f:
        return json.loads(f.read(), object_pairs_hook=OrderedDict)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-c", "--case-dir",
                        default=".",
                        help="Path to case directory.")
    parser.add_argument("--dpi", type=float, default=220)
    return parser.parse_args()


def main():
    args = parse_args()
    run(case_dir=args.case_dir, dpi=args.dpi)


def run(case_dir, dpi, **kwargs):
    config_dir = os.path.join(case_dir, CONFIG_DIR)
    json_files = (PLOT_FORMAT_JSON, POSITIONS_JSON, VARIABLES_JSON)
    json_files = [os.path.join(config_dir, file) for file in json_files]
    plot_format, positions, variables = [read_json_as_ordereddict(file)
                                         for file in json_files]
    plotter = CaseComparisonPlotter(plot_format=plot_format,
                                    case_dir=case_dir,
                                    positions=positions,
                                    variables=variables,
                                    **kwargs)
    fig, axs = plotter.plot()
    output_file = os.path.join(case_dir, "plot.png")
    fig.savefig(output_file, dpi=dpi)


if __name__ == "__main__":
    main()
