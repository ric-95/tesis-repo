import pandas as pd
import os
import glob


def get_csv_files_list(csv_dir):
    """Return a list containing all found csv files within a given directory."""
    return glob.glob(f"{csv_dir}/*.csv")


def csv_to_dataframe(csv_file, **kwargs):
    return pd.read_csv(csv_file, **kwargs)


def parse_openfoam_probe_file_to_dataframe(probe_file):
    raise NotImplementedError


def check_create_dir(dir_):
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    return dir_