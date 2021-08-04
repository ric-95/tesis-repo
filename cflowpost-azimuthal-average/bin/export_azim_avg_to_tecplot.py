import os
import sys
sys.path.append("../")
import azimuthal_average.post as post
import azimuthal_average.common as common
import azimuthal_average.export as export
import pandas as pd
import numpy as np
import tecplot as tp
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--case-dir", type=str,
                    help="OpenFOAM case directory to export",
                    default=".")
args = parser.parse_args()
CASE_DIR = args.case_dir
CSV_FILE = r"slice_csv_files\average_output\azim_average.csv"
CSV_FILE_LOC = os.path.join(CASE_DIR, CSV_FILE)

BLUFF_DIAMETER = 0.06
FREESTREAM_VELOCITY = 11.8


def main():
    print("Reading csv file")
    azim_avg_df = pd.read_csv(CSV_FILE_LOC)
    print("Post processing dataframe")
    post_processed_df = post.process(azim_avg_df,
                                     length_ref=BLUFF_DIAMETER,
                                     u_ref=FREESTREAM_VELOCITY)
    print("Connecting to tecplot")
    var_list = common.tecplot_variables()
    export.to_tecplot(post_processed_df, var_list)
    return


if __name__ == "__main__":
    main()
