from cflowpost.primitive.dataparsing import (check_create_dir,
                                             )
from cflowpost.azimuthal_average import (take_azimuthal_running_average,
                                         process_turbulent_flow_fields,
                                         )
import os
import glob
import argparse

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
NORM_R_KEYS = (f"{r_key}/U_inf^2".replace("z", "x")
               for r_key in R_KEYS)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--case-dir",
                        help="Path to case directory containing the csv dump.",
                        type=str,
                        default=".")
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


def lookup_filepattern(file_pattern,
                       sort=True):
    if sort:
        return sorted(glob.glob(file_pattern))
    return glob.glob(file_pattern)


def run(file_pattern,
        output_file):
    csv_list = lookup_filepattern(file_pattern)
    print(f"Reading csv files in the following order:\n",
          *csv_list,
          sep="\n")
    azim_avg_df = take_azimuthal_running_average(csv_list,
                                                 write_intermediate=False,
                                                 copy=False)
    azim_avg_df = process_turbulent_flow_fields(azim_avg_df,
                                                length_ref=LENGTH_REF,
                                                u_ref=U_REF,
                                                coord_keys=COORD_KEYS,
                                                norm_coord_keys=NORM_COORD_KEYS,
                                                u_keys=U_KEYS,
                                                norm_u_keys=NORM_U_KEYS,
                                                r_keys=R_KEYS,
                                                norm_r_keys=NORM_R_KEYS,)
    output_dir = os.path.dirname(output_file)
    check_create_dir(output_dir)
    azim_avg_df.drop(
        columns="vtkValidPointMask").to_csv(output_file, sep=",", index=False)


def main():
    args = _parse_args()
    case_dir = args.case_dir
    file_pattern = os.path.join(case_dir, args.file_pattern)
    output_file = os.path.join(case_dir, args.output_filename)
    run(file_pattern, output_file)


if __name__ == "__main__":
    main()
