from cflowpost import filehandlers as fh
from thesis.azimuthal_average import (take_azimuthal_running_average, )
from cflowpost.processing import process_turbulent_flow_fields
from cflowpost import pvx
import os
import glob
import argparse
import json

LENGTH_REF = 0.06
U_REF = 11.8
COORD_KEYS = ("r", "z")
NORM_COORD_KEYS = ("r/D_b", "x/D_b")
U_KEYS = ("u_mean_r",
          "u_mean_t",
          "u_mean_z")
NORM_U_KEYS = ("v/U_inf",
               "w/U_inf",
               "u/U_inf")
R_KEYS = ("R_rr",
          "R_tt",
          "R_zz",
          "R_rt",
          "R_tz",
          "R_rz")
NORM_R_KEYS = tuple(f"{r_key}/U_inf^2".replace("z", "x")
                    for r_key in R_KEYS)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--case-dir",
                        help="Path to case directories containing"
                             " the csv dumps.",
                        type=str,
                        default=".",
                        nargs="+")
    parser.add_argument("--file-pattern",
                        help="Glob file pattern to look up relative to"
                             "the case directory specified.",
                        type=str,
                        default="azim_average/raw/SLICE*.csv")
    parser.add_argument("-o", "--output-filename",
                        help="Filename relative to case dir to"
                             " write averaged frame on.",
                        default="azim_average/azim_average.csv")
    return parser.parse_args()


def read_json(json_file, **kwargs):
    with open(json_file, mode="r") as f:
        return json.loads(f.read(), **kwargs)


def lookup_filepattern(file_pattern,
                       sort=True):
    if sort:
        return sorted(glob.glob(file_pattern))
    return glob.glob(file_pattern)


def extract_lines_from_processed_slice(slice_csv, line_config_json,
                                       x_col="r/D_b", y_col="x/D_b",
                                       z_col="t"):
    extraction_config = pvx.extraction_json_to_config(line_config_json)
    slice_source = pvx.csv_source(slice_csv, x_col=x_col,
                                  y_col=y_col, z_col=z_col)
    output_dir = os.path.dirname(slice_csv)
    pvx.extract(extraction_config=extraction_config,
                source_config=slice_source,
                output_dir=output_dir,
                )


def run(file_pattern,
        output_file):
    csv_list = lookup_filepattern(file_pattern)
    print(f"Reading csv files in the following order:\n",
          *csv_list,
          sep="\n")
    azim_avg_df = take_azimuthal_running_average(csv_list,
                                                 write_intermediate=False,
                                                 copy=False)
    print("Finished averaging.")
    azim_avg_df = process_turbulent_flow_fields(azim_avg_df,
                                                length_ref=LENGTH_REF,
                                                u_ref=U_REF,
                                                coord_keys=COORD_KEYS,
                                                norm_coord_keys=NORM_COORD_KEYS,
                                                u_keys=U_KEYS,
                                                norm_u_keys=NORM_U_KEYS,
                                                r_keys=R_KEYS,
                                                norm_r_keys=NORM_R_KEYS,)
    azim_avg_df["t"] = 0
    output_dir = os.path.dirname(output_file)
    fh.check_create_dir(output_dir)
    azim_avg_df.drop(
        columns="vtkValidPointMask").to_csv(output_file, sep=",", index=False)
    x_col, y_col = NORM_COORD_KEYS
    z_col = "t"
    cwd = os.path.dirname(__file__)
    line_config_file = os.path.join(cwd, "line_extraction_config.json")
    line_config = read_json(line_config_file)
    extract_lines_from_processed_slice(output_file,
                                       x_col=x_col,
                                       y_col=y_col,
                                       z_col=z_col,
                                       line_config_json=line_config)


def main():
    args = _parse_args()
    case_dirs = args.case_dir
    for case_dir in case_dirs:
        file_pattern = os.path.join(case_dir, args.file_pattern)
        output_file = os.path.join(case_dir, args.output_filename)
        run(file_pattern, output_file)


if __name__ == "__main__":
    main()
