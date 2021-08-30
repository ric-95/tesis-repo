import os
import glob
import re

import matplotlib.axes
import numpy as np
import pandas as pd
from toolz.itertoolz import groupby
from cflowpost import filehandlers as fh
from cflowpost import datatypes as dt
from cflowpost.xcorr import \
    SignalStackXCorrelationFunction as TwoPointCorrelationFunction
from typing import List, Mapping, Sequence
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from cflowpost.plotting import NumericalValidation1DPlotter
from cflowpost import plotting as cfplot
from thesis.two_point_corr import (compute_two_point_correlation,
                                   plot_sample_independence)

Sample = Sequence[pd.DataFrame]
SamplesMapping = Mapping[str, Sample]
VectorKeys = List[str]
PI = np.pi


def run(sample_file_list,
        file_regex_pattern,
        sample_id_key,
        transient_u_keys: VectorKeys,
        mean_u_keys: VectorKeys,
        tpc_keys: VectorKeys,
        arc_length,
        converged_plot_file="TwoPointCorrelation.png",
        sample_independence_file="SampleIndependence.png",
        tpc_df_file="TwoPointCorrelation.csv",
        dpi=200):
    samples_mapping = retrieve_samples(sample_file_list,
                                       file_regex_pattern,
                                       sample_id_key)
    samples_mapping = cleanup_samples(samples_mapping)
    transient_samples_stack = transform_samples_to_cylindrical_stack(
        samples_mapping, transient_u_keys)
    last_timestep = max(samples_mapping.keys())
    last_sample = samples_mapping[last_timestep]
    u_mean = calculate_average_velocity(last_sample, mean_u_keys)
    fluctuations_stack = calculate_fluctuations(transient_samples_stack,
                                                u_mean)
    tpc_df = compute_two_point_correlation(fluctuations_stack,
                                           arc_length,
                                           zero_padded=True,
                                           tpc_keys=tpc_keys)
    tpc_df.to_csv(tpc_df_file, sep=",")
    plot_two_point_correlation(tpc_df,
                               output_file=converged_plot_file,
                               dpi=dpi)
    plot_sample_independence(fluctuations_stack,
                             arc_length,
                             tpc_keys,
                             sample_independence_file,
                             dpi=dpi)


def retrieve_samples(sample_dump,
                     regex_pattern,
                     id_key,
                     **kwargs) -> SamplesMapping:
    """Retrieves the extracted samples assumed to be stored as csv files.

    Parameters
    ----------
    sample_dump : List[str]
        List of file locations.
    regex_pattern : re.Pattern
        Compiled regex pattern to identify samples
    id_key : str
        Key to used to group samples in regex pattern.

    Returns
    -------
    SamplesMapping
    """
    sample_dump = sorted(sample_dump)
    sample_mapping = _group_strings_by_regex_key(sample_dump,
                                                 regex_pattern,
                                                 id_key)
    keys = sorted(list(sample_mapping.keys()))
    return {key: _read_csv_list(sample_mapping[key], **kwargs) for key in keys}


def cleanup_samples(samples_mapping: SamplesMapping) -> SamplesMapping:
    return {sample_id: [df.interpolate(method="linear", inplace=False,)
                        for df in sample]
            for sample_id, sample in samples_mapping.items()}


def transform_samples_to_cylindrical_stack(samples_mapping: SamplesMapping,
                                           u_keys: VectorKeys):
    """

    Parameters
    ----------
    samples_mapping : SamplesMapping
    u_keys : VectorKeys

    Returns
    -------
    np.ndarray
    """
    return np.concatenate([transform_sample_to_cylindrical(sample, u_keys)
                           for sample in samples_mapping.values()])


def transform_sample_to_cylindrical(sample: Sample,
                                    vector_keys: VectorKeys) -> np.ndarray:
    total_lines = len(sample)
    thetas = np.arange(total_lines)/total_lines*2*PI
    return np.stack([transform_line_to_cylindrical(line, vector_keys, theta)
                     for line, theta in zip(sample, thetas)])


def transform_line_to_cylindrical(line: pd.DataFrame,
                                  vector_keys: VectorKeys,
                                  theta: float):
    cart_stack = dt.CartesianVectorStack(line[vector_keys].to_numpy())
    return cart_stack.convert_to_cylindrical(theta).to_array()


def calculate_average_velocity(sample: Sample, vector_keys: VectorKeys):
    cyl_stack = transform_sample_to_cylindrical(sample, vector_keys)
    return _average_lines(cyl_stack)


def calculate_fluctuations(transient, mean):
    return transient - mean


def plot_two_point_correlation(tpc_df: pd.DataFrame,
                               ax: matplotlib.axes.Axes = None,
                               grid=True,
                               output_file="",
                               dpi=200,
                               title="",
                               **kwargs) -> matplotlib.axes.Axes:
    if ax is None:
        fig, ax = plt.subplots(1, 1)
    ax.plot(tpc_df, **kwargs)
    ax.minorticks_on()
    labels = tpc_df.columns
    plotter = NumericalValidation1DPlotter(
        num_x=tpc_df.index.to_numpy(),
        num_y=tpc_df.to_numpy(),
        num_labels=labels,

    )
    ax.axhline(0.3, c="tab:orange", linestyle="--")
    ax.axhline(0, c="tab:gray", linestyle="--")
    ax.legend(labels=tpc_df.columns)
    if grid:
        ax.grid(which='both')
        ax.grid(which="minor",
                linestyle="--",
                linewidth=0.5,)
    if title:
        ax.title(title)
    if output_file:
        ax.figure.savefig(output_file, dpi=dpi, )
    return ax


def _average_lines(stack):
    return np.nanmean(stack, axis=0)


def _group_strings_by_regex_key(strings: List[str],
                                regex_pattern: re.Pattern,
                                group_key: str) -> Mapping[str, str]:
    """Groups a list of strings according to a regex pattern and a grouping key.
    The pattern must look for the grouping key.

    Parameters
    ----------
    strings : List[str]
    regex_pattern : re.Pattern
    group_key : str

    Returns
    -------
    Mapping[str, str]
    """
    return dict(
        groupby(key=lambda str_: regex_pattern.search(str_).group(group_key),
                seq=strings))


def _read_grouped_sample(grouped_sample: dict):
    keys = sorted(list(grouped_sample.keys()))
    return {key: _read_csv_list(grouped_sample[key]) for key in keys}


def _read_csv_list(csv_list, **kwargs):
    return [fh.csv_to_dataframe(csv_file, **kwargs) for csv_file in csv_list]


def _get_csv_list(dir_: str, glob_pattern: str = "*.csv") -> List[str]:
    return glob.glob(os.path.join(dir_, glob_pattern))


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument("--csv-dump-dir",
                        type=str,
                        help="Path to directory containing csv dump.")
    parser.add_argument("--regex-pattern",
                        type=str,
                        help="Pattern to look for in csv. Must contain a"
                             " named group to identify the sample.",
                        default="T=(?P<time>[0-9.]{3})_LINE(?P<line>[0-9]{3})")
    parser.add_argument("--sample-id-key",
                        type=str,
                        help="Key which identifies the sample each file "
                             "belongs to in regex pattern.",
                        default="time")
    parser.add_argument("--transient-u-keys",
                        type=str,
                        nargs="+",
                        help="Transient velocity keys in X-Y-Z order.",
                        default=["U_0", "U_1", "U_2"])
    parser.add_argument("--mean-u-keys",
                        type=str,
                        nargs="+",
                        help="Mean velocity keys in X-Y-Z order.",
                        default=["UMean_0", "UMean_1", "UMean_2"])
    parser.add_argument("--tpc-keys", type=str, nargs="+",
                        help="Two point correlation keys R-T-Z order.",
                        default=["B_vv", "B_ww", "B_uu"])
    parser.add_argument("--arc-length",
                        type=float,
                        help="Arc length of lines extracted.")
    parser.add_argument("--output-dir",
                        type=str,
                        help="Path to directory to store output files.",
                        default=".")
    return parser.parse_args()


def main():
    args = _parse_args()
    dump_dir = args.csv_dump_dir
    sample_file_list = _get_csv_list(dump_dir)
    regex_pattern = re.compile(args.regex_pattern)
    sample_id_key = args.sample_id_key
    transient_u_keys = args.transient_u_keys
    mean_u_keys = args.mean_u_keys
    tpc_keys = args.tpc_keys
    arc_length = args.arc_length
    assert arc_length is not None, "Please input an arc length."
    output_dir = args.output_dir
    converged_plot_file = f"{output_dir}/twopointcorr.png"
    sample_independence_plot_file = f"{output_dir}/sampleind_twopointcorr.png"
    csv_file = f"{output_dir}/twopointcorr.csv"
    run(sample_file_list,
        regex_pattern,
        sample_id_key,
        transient_u_keys,
        mean_u_keys,
        tpc_keys,
        arc_length,
        converged_plot_file,
        sample_independence_plot_file,
        csv_file)
    return


if __name__ == "__main__":
    main()
