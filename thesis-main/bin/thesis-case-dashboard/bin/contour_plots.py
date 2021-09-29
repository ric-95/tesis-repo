import pandas as pd
import matplotlib.pyplot as plt
from thesis.plotting import ContourPlotter, ContourValidationPlotter
from typing import Sequence, Tuple
import argparse
import json
import os

Key = str
Keys = Sequence[Key]
Path = str


X_COL = "r/D_b"
Y_COL = "x/D_b"
U_COL = "v/U_inf"
PLOTTING_U_COL = f"r-{U_COL}"
V_COL = "u/U_inf"
K_COL = "k/U_inf^2"
RADIAL_COMPONENTS_TO_TRANSFORM = [
    PLOTTING_U_COL,
    "R_rx/U_inf^2",
    "R_rt/U_inf^2",
]
RADIAL_STRESS_COL = "R_rr/U_inf^2"
CONTOUR_COLS = [
    V_COL,
    PLOTTING_U_COL,
    "k/U_inf^2",
    "R_xx/U_inf^2",
    RADIAL_STRESS_COL,
    "R_rx/U_inf^2",
    "R_rt/U_inf^2",
    "R_tx/U_inf^2",
    "-II",
    "III",
]
TITLES = [
    r"$u/U_{\infty}$",
    r"$v/U_{\infty}$",
    r"$k/U_{\infty}^2$",
    r"$R_{xx}/U_{\infty}^2$",
    r"$R_{rr}/U_{\infty}^2$",
    r"$R_{rx}/U_{\infty}^2$",
    r"$R_{rt}/U_{\infty}^2$",
    r"$R_{tx}/U_{\infty}^2$",
    r"$-II$",
    r"$III$",
]
SHAPE = (2, 5)
BASEWIDTH = 4
BASEHEIGHT = 3.2


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file", type=Path, help="Path to config json file."
    )
    parser.add_argument(
        "--exp-csv", type=Path, help="Path to experimental data in csv format."
    )
    parser.add_argument(
        "--num-csv", type=Path, help="Path to numerical data in csv format."
    )
    parser.add_argument("--output-dir", default=".", type=Path)
    parser.add_argument("--dpi", default=220, type=float)
    return parser.parse_args()


def run(
    num_df: pd.DataFrame,
    exp_df: pd.DataFrame,
    contour_cols: Keys,
    levels: int,
    shape: Tuple[int, int],
    x_col: Key = X_COL,
    y_col: Key = Y_COL,
    u_col: Key = U_COL,
    v_col: Key = V_COL,
    titles: Sequence[str] = None,
    contour_plotter_args: dict = None,
    basewidth=4,
    baseheight=3.2,
    output_file="contour-plots.png",
    dpi=220,
):
    nrows, ncols = shape
    figwidth = basewidth * ncols
    figheight = baseheight * nrows
    figsize = (figwidth, figheight)
    fig, axs = plt.subplots(
        nrows, ncols, sharex="all", sharey="all", figsize=figsize
    )
    contour_plotter = create_contour_plotter(
        x_col,
        y_col,
        u_col,
        v_col,
        contour_cols[0],
        levels,
        **contour_plotter_args,
    )
    validation_plotter = ContourValidationPlotter(
        contour_plotter, num_df, exp_df
    )
    for contour_col, title, ax in zip(contour_cols, titles, axs.ravel()):
        validation_plotter.update_contour_column(contour_col)
        new_max = exp_df[contour_col].max()
        new_min = exp_df[contour_col].min()
        validation_plotter.update_contourf_args(vmin=new_min, vmax=new_max)
        validation_plotter.plot(ax=ax)
        ax.set_title(title)
    fig.savefig(output_file, dpi=dpi)


def main():
    args = _parse_args()
    num_df = read_slice(args.num_csv)
    exp_df = read_slice(args.exp_csv)
    exp_df = exp_df[exp_df[X_COL] < 0]
    config = read_config(config_file=args.config_file)
    titles = config.get("titles", TITLES)
    shape = config.get("shape", SHAPE)
    levels = config.get("levels", 6)
    streamplot_args = config.get("streamplot_args", {})
    contourf_args = config.get("contourf_args", {})
    contour_plotter_args = {
        "streamplot_args": streamplot_args,
        "contourf_args": contourf_args,
    }
    basewidth = config.get("basewidth", BASEWIDTH)
    baseheight = config.get("baseheight", BASEHEIGHT)
    output_file = os.path.join(args.output_dir, "contour-plots.png")
    dpi = args.dpi
    print(num_df)
    run(
        num_df,
        exp_df,
        contour_cols=CONTOUR_COLS,
        titles=titles,
        shape=shape,
        levels=levels,
        contour_plotter_args=contour_plotter_args,
        basewidth=basewidth,
        baseheight=baseheight,
        output_file=output_file,
        dpi=dpi,
    )


def read_slice(slice_csv: Path, **kwargs):
    df = pd.read_csv(slice_csv, **kwargs)
    df[PLOTTING_U_COL] = df[U_COL]
    df = convert_radial_components_in_negative_r(
        df, r_col=X_COL, radial_components=RADIAL_COMPONENTS_TO_TRANSFORM
    )
    return df


def convert_radial_components_in_negative_r(
    df: pd.DataFrame, r_col: Key, radial_components: Keys
):
    df = df.copy()
    negative_r = df[r_col] < 0
    df.loc[negative_r, radial_components] *= -1
    return df


def read_config(config_file: Path):
    with open(config_file, "r") as f:
        return json.loads(f.read())


def create_contour_plotter(
    x_col: Key,
    y_col: Key,
    u_col: Key,
    v_col: Key,
    contour_col: Key,
    levels: int,
    **kwargs,
):
    return ContourPlotter(
        x_col=x_col,
        y_col=y_col,
        u_col=u_col,
        v_col=v_col,
        contour_col=contour_col,
        levels=levels,
        **kwargs,
    )


if __name__ == "__main__":
    main()
