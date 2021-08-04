from cflowpost.primitive.dataparsing import check_create_dir
import os
import glob
from cflowpost.azimuthal_average import take_azimuthal_running_average
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--case-dir",
                    help="Path to OpenFOAM case directory.",
                    type=str, default=".")
parser.add_argument("--file-pattern",
                    help="Glob file pattern to look up relative to"
                         "the case dir specified.",
                    type=str, default="azim_average/raw/SLICE*.csv")
parser.add_argument("-o", "--output-filename",
                    help="Filename relative to case dir to"
                         " write averaged frame on.",
                    default="azim_average/azim_average.csv")
args = parser.parse_args()
CASE_DIR = args.case_dir
FILE_PATTERN = os.path.join(CASE_DIR, args.file_pattern)


def main():
    csv_list = sorted(glob.glob(FILE_PATTERN))
    print(f"Reading csv files in the following order:\n", *csv_list, sep="\n")
    azim_avg_df = take_azimuthal_running_average(csv_list, write_intermediate=False,
                                                 copy=False)
    output_file = os.path.join(CASE_DIR, args.output_filename)
    output_dir = os.path.dirname(output_file)
    check_create_dir(output_dir)
    azim_avg_df.to_csv(output_file, sep=",")
    return


if __name__ == "__main__":
    main()
