import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cflowpost.xcorr import \
    SignalStackXCorrelationFunction as TwoPointCorrelationFunction
import cflowpost.plotting as cfplot


def compute_two_point_correlation(fluct_stack, arc_length,
                                  zero_padded=True,
                                  tpc_keys=None):
    index_length = 1
    if arc_length is not None:
        index_length = arc_length / fluct_stack.shape[1]

    tpc_func = TwoPointCorrelationFunction(fluct_stack, index_length,
                                           zero_padded=zero_padded)
    points_per_line = fluct_stack.shape[1]
    x_ast = np.linspace(0, arc_length, points_per_line)
    df = pd.DataFrame(data={"x_ast": x_ast})
    if tpc_keys is None:
        tpc_keys = ["B_uu", "B_vv", "B_ww"]
    tpc = tpc_func(x_ast)
    df.loc[:, tpc_keys] = tpc
    return df.set_index("x_ast")


def plot_sample_independence(fluct_stack,
                             arc_length,
                             tpc_keys,
                             output_file="",
                             figwidth=8,
                             height_to_width_ration=0.5,
                             random_state=0,
                             zero_padded=True,
                             **kwargs):
    total_sample_size = len(fluct_stack)
    if total_sample_size % 2 != 0:
        total_sample_size -= 1
    sample_sizes = []
    sample_size = total_sample_size
    while sample_size >= 1:
        sample_sizes.append(sample_size)
        sample_size = int(sample_size/2)
    total_plots = len(tpc_keys)
    figheight = figwidth*height_to_width_ration*total_plots
    fig, axs = plt.subplots(total_plots, 1, figsize=(figwidth, figheight))
    index_array = np.arange(total_sample_size)
    np.random.RandomState(random_state)
    random_indices = np.random.choice(index_array, total_sample_size)
    sampled_tpc_df_mapping = {
        sample_size: _sampled_tpc(fluct_stack,
                                  random_indices[:sample_size],
                                  arc_length,
                                  zero_padded=zero_padded)
        for sample_size in sample_sizes}
    num_x = np.column_stack(
        [sampled_tpc_df_mapping[sample_size].index.to_numpy()
         for sample_size in sample_sizes[::2]])
    for key, ax in zip(tpc_keys, axs):
        num_y = np.column_stack(
            [sampled_tpc_df_mapping[sample_size][key].to_numpy()
             for sample_size in sample_sizes[::2]])
        num_y_labels = [f"{sample_size} lines"
                        for sample_size in sample_sizes[::2]]
        ax = cfplot.plot1d_numerical_validation(
            numerical_x=num_x, numerical_y=num_y,
            numerical_labels=num_y_labels, ax=ax)
        ax.set_title(key)
    fig.subplots_adjust(top=0.97, bottom=0.03)
    if output_file:
        fig.savefig(output_file, **kwargs)


def _sampled_tpc(fluct_stack, sample_indices, arc_length, zero_padded):
    sampled_flucts = fluct_stack[sample_indices]
    return compute_two_point_correlation(sampled_flucts,
                                         arc_length,
                                         zero_padded)