#!/home/ricardo/miniconda3/envs/tesis-env/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cflowpost import plotting as cfplot
import argparse
from typing import Sequence, Mapping
import json
from tqdm import tqdm


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-data-files",
                        nargs="+",
                        help="Paths pointing to numerical data files to plot")
    parser.add_argument("--exp-data-files",
                        nargs="+",
                        help="Paths pointing to experimental data"
                             " files to plot.")
    parser.add_argument("--labels",
                        nargs="+",
                        help="Labels to associate to each line.")
    parser.add_argument("--config-file",
                        help="Path to configuration file")
    parser.add_argument("--output-file", default="./line_plots.png")
    parser.add_argument("--dpi", default=220, help="Figure DPI.")
    return parser.parse_args()


def main():
    args = _parse_args()
    config = read_json(args.config_file)

    layout_config = config["layout"]
    numerical_frames = [pd.read_csv(file) for file in args.num_data_files]
    experimental_frames = [pd.read_csv(file) for file in args.exp_data_files]
    labels = args.labels
    num_data_map = _build_data_mapping(labels, numerical_frames)
    exp_data_map = _build_data_mapping(labels, experimental_frames)
    x_layout = parse_layout_config(layout_config, "x")
    y_layout = parse_layout_config(layout_config, "y")
    title_layout = parse_layout_config(layout_config, "title")
    ylabels_layout = parse_layout_config(layout_config, "ylabel")
    xlabels_layout = parse_layout_config(layout_config, "xlabel")
    xlims_layout = parse_layout_config(layout_config, "xlim")
    dpi = args.dpi
    run(numerical_data_mapping=num_data_map,
        experimental_data_mapping=exp_data_map,
        labels=labels,
        x_var_layout=x_layout,
        xlabels_layout=xlabels_layout,
        y_var_layout=y_layout,
        ylabels_layout=ylabels_layout,
        titles_layout=title_layout,
        xlims_layout=xlims_layout,
        dpi=dpi)


def _build_data_mapping(keys, frames):
    return {key: frame for key, frame in zip(keys, frames)}


def run(numerical_data_mapping: Mapping[str, pd.DataFrame],
        experimental_data_mapping: Mapping[str, pd.DataFrame],
        labels: Sequence[str],
        x_var_layout,
        xlabels_layout,
        y_var_layout: Sequence[str],
        ylabels_layout,
        titles_layout,
        xlims_layout,
        basewidth=4.5,
        baseheight=5.7,
        tight=True,
        output_filename="line_profiles.png",
        **kwargs):
    x_var_layout = np.atleast_2d(x_var_layout)
    xlabels_layout = np.atleast_2d(xlabels_layout)
    y_var_layout = np.atleast_2d(y_var_layout)
    ylabels_layout = np.atleast_2d(ylabels_layout)
    xlims_layout_arr = np.asarray(xlims_layout,)
    titles_layout = np.atleast_2d(titles_layout)
    layouts = (x_var_layout, y_var_layout)
    for layout in layouts:
        assert layout.ndim == 2, "Maximum of 2 dimensions please"
    assert (x_var_layout.shape == y_var_layout.shape), "Layout shape mismatch."
    assert (x_var_layout.shape == titles_layout.shape), "Layout shape mismatch"
    rows, cols = x_var_layout.shape
    fig, axs = plt.subplots(rows, cols,
                            figsize=(basewidth*cols, baseheight*rows))
    plotting_iterator = tqdm(zip(x_var_layout.ravel(),
                                 y_var_layout.ravel(),
                                 xlabels_layout.ravel(),
                                 ylabels_layout.ravel(),
                                 xlims_layout_arr.reshape(-1, 2),
                                 titles_layout.ravel(),
                                 axs.ravel()))
    for (x_var, y_var, xlabel,
         ylabel, xlim, title, ax) in plotting_iterator:
        num_x = np.column_stack([numerical_data_mapping.get(label)[x_var]
                                 for label in labels])
        num_y = np.column_stack([numerical_data_mapping.get(label)[y_var]
                                 for label in labels])
        exp_x = np.column_stack([experimental_data_mapping.get(label)[x_var]
                                 for label in labels])
        exp_y = np.column_stack([experimental_data_mapping.get(label)[y_var]
                                 for label in labels])
        num_labels = [label.strip("'") for label in labels]
        exp_labels = [f"Exp. {label}" for label in num_labels]
        cfplot.plot1d_numerical_validation(numerical_x=num_x,
                                           numerical_y=num_y,
                                           numerical_labels=num_labels,
                                           experimental_labels=exp_labels,
                                           experimental_x=exp_x,
                                           experimental_y=exp_y,
                                           title=title,
                                           ax=ax,)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xlim(xlim[0], xlim[1])
    if tight:
        fig.tight_layout()
    fig.savefig(output_filename, **kwargs)
    return fig


def parse_layout_config(layout_obj, var):
    layout = []
    for item in layout_obj:
        inner = []
        if type(item) == list:
            for i in item:
                inner.append(i[var])
            layout.append(inner)
        elif type(item) == dict:
            layout.append(item[var])
    return layout


def read_json(json_file, **kwargs):
    with open(json_file, "r") as f:
        return json.loads(f.read(), **kwargs)


if __name__ == "__main__":
    main()
