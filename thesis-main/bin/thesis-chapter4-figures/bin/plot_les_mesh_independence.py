import argparse
from cflowpost import plotting
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import Mapping, List
from collections import OrderedDict

Path = str
Key = str
Label = str
FrameMapping = Mapping[Label, pd.DataFrame]


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str,
                        help="Series of files containing the two point "
                             "correlation functions to compare.",
                        nargs="+")
    parser.add_argument("--labels", type=str,
                        help="Labels to apply to the inputs. Must be in the "
                             "same order as the inputs given.",
                        nargs="+")
    parser.add_argument("--tpc-keys", type=str,
                        help="Keys corresponding to the relevant components to"
                             "contrast.",
                        nargs="+",
                        default=["B_uu", "B_vv", "B_ww"])
    parser.add_argument("--yaxis-labels", nargs="+",
                        default=["$B_{uu}$",
                                 "$B_{vv}$",
                                 "$B_{ww}$", ],
                        help="Series of labels")
    parser.add_argument("--index-key", type=str, default="x_ast",
                        help="Key containing the input values to "
                             "the two point correlation function.")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to save plot in.")
    parser.add_argument("--dpi", type=float, default=220)
    parser.add_argument("--figwidth", type=float, default=6,
                        help="Figure width in inches.")
    parser.add_argument("--height-to-width-ratio", type=float, default=0.5)
    parser.add_argument("--figtitle",
                        type=str,
                        default="LES Mesh Independence",
                        help="Figure title")
    return parser.parse_args()


def main():
    args = _parse_args()
    valid_label_input = ((len(args.inputs) == len(args.labels))
                         and args.labels is not None)
    assert valid_label_input, "Labels must match input files."
    labels = args.labels
    if labels is None:
        labels = list(range(len(args.inputs)))
    tpc_mapping = OrderedDict(
        {label: pd.read_csv(file).set_index(args.index_key)
         for label, file in zip(labels, args.inputs)})
    tpc_keys = args.tpc_keys
    ylabels = args.yaxis_labels
    figwidth = args.figwidth
    figtitle = args.figtitle
    height_to_width_ratio = args.height_to_width_ratio
    output_file = os.path.join(args.output_dir, "les_mesh_independence.png")
    run(tpc_mapping=tpc_mapping,
        tpc_keys=tpc_keys,
        ylabels=ylabels,
        figwidth=figwidth,
        figtitle=figtitle,
        height_to_width_ratio=height_to_width_ratio,
        output_file=output_file, )
    return


def run(tpc_mapping: FrameMapping,
        tpc_keys: List[Key],
        ylabels,
        figwidth=5,
        figtitle="",
        height_to_width_ratio=0.5,
        dpi=220,
        output_file="./MeshIndependence.png"
        ):
    labels = list(tpc_mapping.keys())
    num_x = np.asarray([tpc_mapping[label].index.to_numpy()
                        for label in labels])
    num_ys = [np.asarray([tpc_mapping[label][tpc_key].to_numpy()
                          for label in labels]) for tpc_key in tpc_keys]
    n_plots = len(tpc_keys)
    figheight = figwidth*height_to_width_ratio*n_plots
    fig, axs = plt.subplots(n_plots, 1, figsize=(figwidth, figheight),
                            sharey="all", sharex="all")
    for tpc_key, num_y, ylabel, ax in zip(tpc_keys, num_ys, ylabels, axs, ):
        plotting.plot1d_numerical_validation(numerical_x=num_x.T,
                                             numerical_y=num_y.T,
                                             numerical_labels=labels,
                                             ax=ax,)
        ax.set_ylabel(ylabel,
                      rotation="horizontal",
                      usetex=False,
                      fontsize="large")
        ax.axhline(0.3, c="tab:red", linestyle=":", )
        ax.axhline(0, c="tab:gray", linestyle=":", )
        ax.minorticks_on()
    axs[-1].set_xlabel("$x^{*}$", usetex=False, fontsize="large")
    if figtitle:
        fig.suptitle(figtitle, fontsize="x-large")
    fig.tight_layout()
    fig.savefig(output_file, dpi=dpi)
    return fig



if __name__ == "__main__":
    main()
