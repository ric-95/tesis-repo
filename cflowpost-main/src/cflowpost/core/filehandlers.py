import pandas as pd
import dask.dataframe as dd
import os
import glob


def get_csv_files_list(csv_dir):
    """Return a list containing all found csv files within a given directory."""
    return glob.glob(f"{csv_dir}/*.csv")


def get_files_by_pattern(pattern):
    return glob.glob(pattern)


def csv_to_dataframe(csv_file, backend="pandas", **kwargs):
    if backend == "pandas":
        return pd.read_csv(csv_file, **kwargs)
    elif backend == "dask":
        return dd.read_csv(csv_file, **kwargs)


def check_create_dir(dir_):
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    return dir_
