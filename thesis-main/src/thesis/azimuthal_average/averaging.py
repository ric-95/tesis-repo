import os
import pandas as pd
import numpy as np
from tqdm import tqdm

from cflowpost import datatypes as dt
from cflowpost.core import filehandlers as fh
from typing import List


def _umean_coords(corrds):
    return tuple(f"u_mean_{coord}" for coord in corrds)


CARTESIAN_COORDS = ("x", "y", "z")
CYLINDRICAL_COORDS = ("r", "t", "z")
UMEAN_CART_COORDS = _umean_coords(CARTESIAN_COORDS)
PARAVIEW_CART_COORDS = tuple(f"Points_{i}" for i in range(3))
PARAVIEW_UMEAN_CART_COORDS = tuple(f"UMean_{i}" for i in range(3))
PARAVIEW_R_STRESS_CART_COORDS = tuple(f"UPrime2Mean_{i}" for i in range(6))

R_STRESS_CYL_COORDS = ("R_rr", "R_rt", "R_rz", "R_tt", "R_tz", "R_zz")
UMEAN_CYL_COORDS = _umean_coords(CYLINDRICAL_COORDS)


def take_azimuthal_average(df_list,
                           write_intermediate=False,
                           copy=True):
    raise NotImplementedError


def take_azimuthal_running_average(csv_list: List[str],
                                   write_intermediate=False,
                                   copy=True):
    """Take the azimuthal average of all the csv files within a given directory.

    Parameters
    ----------
        csv_list : List[str]
            List of csv files containing the azimuthal data. Assumes azimuthal
            slices extracted at uniform angles.
        write_intermediate : bool
            If true will write transformed slices
        copy : bool
            If true will work on copies of read dataframes.

    Returns
    -------
    pd.DataFrame
        Frame containing the averaged data."""
    total_slices = len(csv_list)
    assert total_slices > 0, "No files given."
    running_average = None
    for slice_number, csv_file in tqdm(enumerate(csv_list), total=total_slices):
        slice_df = fh.csv_to_dataframe(csv_file)
        theta = calculate_slice_theta(slice_number,
                                      total_slices)
        cylindrical_slice_df = process_slice(
            slice_df, slice_number, theta, copy,
            write_intermediate)
        if running_average is None:
            running_average = cylindrical_slice_df
        running_average = update_running_average(cylindrical_slice_df,
                                                 running_average,
                                                 slice_number+1)
    cols = cylindrical_slice_df.columns
    idx = cylindrical_slice_df.index
    return pd.DataFrame(data=running_average, columns=cols, index=idx)


def write_intermediate_file(dir_, slice_number, slice_):
    fh.check_create_dir(dir_)
    intermediate_file = f"cyl_clice_{slice_number}.csv"
    intermediate_file = os.path.join(dir_, intermediate_file)
    slice_.to_csv(intermediate_file, sep=",")


def update_running_average(new_obs, running_average, n):
    """Updates a running average while avoiding large values
     and provoke overflow.

    Parameters
    ----------
    running_average: value of the cumulative average so far
    n: Number of samples including new observation
    new_obs: New observation"""
    a = 1/n
    b = 1 - a
    return a*new_obs + b*running_average


def process_slice(slice_df, slice_number, theta, copy=True,
                  write_intermediate=False, csv_dir="."):
    cylindrical_slice_df = transform_df_to_cylindric_coordinates(
        slice_df, theta, copy)
    if write_intermediate:
        intermediate_dir = os.path.join(csv_dir, "intermediate")
        write_intermediate_file(intermediate_dir,
                                slice_number,
                                cylindrical_slice_df)
    return cylindrical_slice_df


def calculate_slice_theta(slice_number, total_slices):
    return (slice_number/total_slices)*np.pi*2


def transform_df_to_cylindric_coordinates(dataframe,
                                          theta,
                                          copy=True):
    """Transforms dataframe to cylindrical coordinates

    Args:
        dataframe (DataFrame): Dataframe containing a cartesian slice
        theta (float): Angle of rotation in radians."""
    """Initialize output df"""
    if copy:
        transformed_df = dataframe.copy()
    else:
        transformed_df = dataframe
    coords_df = transform_coordinates_to_cylindrical(dataframe)
    u_cyl_df = transform_velocity_to_cylindrical(dataframe, theta)
    r_cyl_df = transform_stress_tensor_to_cylindrical(dataframe, theta)
    dfs_to_concat = [coords_df, u_cyl_df, r_cyl_df]
    transformed_df = pd.concat([transformed_df, *dfs_to_concat], axis=1)
    wall_shear_stress_labels = [f"wallShearStressMean_{i}" for i in range(3)]
    return transformed_df.drop(
        columns=[
            "Points_Magnitude",
            "UMean_Magnitude",
            "UPrime2Mean_Magnitude",
            "wallShearStressMean_Magnitude",
            "yPlusMean",
            "Point ID",
            *PARAVIEW_CART_COORDS,
            *wall_shear_stress_labels,
            *PARAVIEW_R_STRESS_CART_COORDS,
            *PARAVIEW_UMEAN_CART_COORDS
        ],
        errors="ignore"
    )


def transform_coordinates_to_cylindrical(dataframe):
    cart_pos_array = dataframe[list(PARAVIEW_CART_COORDS)].to_numpy()
    cart_pos_vectors = dt.CartesianVectorStack(cart_pos_array)
    radial_pos = np.sqrt(cart_pos_vectors.x**2 + cart_pos_vectors.y**2)
    axial_pos = cart_pos_vectors.z
    return pd.DataFrame(data={"r": radial_pos, "z": axial_pos})


def transform_velocity_to_cylindrical(dataframe, theta):
    u_keys = list(PARAVIEW_UMEAN_CART_COORDS)
    u_array = dataframe[u_keys].to_numpy()
    u_cart_vectors = dt.CartesianVectorStack(vector_array=u_array)
    return (u_cart_vectors
            .convert_to_cylindrical(theta=theta)
            .as_dataframe(prefix="u_mean"))


def transform_stress_tensor_to_cylindrical(dataframe, theta):
    cart_stress_tensors = dt.SymmetricCartesianTensorStack(
        dataframe[list(PARAVIEW_R_STRESS_CART_COORDS)].to_numpy()
    )
    cyl_stress_tensors = cart_stress_tensors.convert_to_cylindrical(theta)
    return cyl_stress_tensors.as_dataframe(prefix="R")
