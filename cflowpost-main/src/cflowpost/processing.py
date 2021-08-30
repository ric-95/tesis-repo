from . import datatypes as dt
import numpy as np


def process_turbulent_flow_fields(df,
                                  length_ref,
                                  u_ref,
                                  coord_keys,
                                  norm_coord_keys,
                                  u_keys,
                                  norm_u_keys,
                                  r_keys,
                                  norm_r_keys):
    """Given a dataframe, processes turbulent flow data referenced by the
    provided keys.

    This function will:

    - Non-dimensionalize the flow velocity and turbulent statistics as well
      as the coordinate system.

    - Compute the second and third invariants of the anisotropy tensor.

    Parameters
    ----------
    df : pandas.DataFrame
    length_ref : float
    u_ref : float
    coord_keys : List[str]
    norm_coord_keys : list[str]
    u_keys : List[str]
    norm_u_keys : List[str]
    r_keys : List[str]
    norm_r_keys : List[str]

    Returns
    -------
    pandas.DataFrame
    """
    coord_keys = list(coord_keys)
    norm_coord_keys = list(norm_coord_keys)
    u_keys = list(u_keys)
    norm_u_keys = list(norm_u_keys)
    r_keys = list(r_keys)
    norm_r_keys = list(norm_r_keys)
    df = normalize_coordinates(df,
                               coord_keys,
                               norm_coord_keys,
                               length_ref)
    norm_slice_df = flow_vars(df,
                              u_keys=u_keys,
                              r_keys=r_keys,
                              norm_u_keys=norm_u_keys,
                              norm_r_keys=norm_r_keys,
                              u_reference=u_ref)
    post_df = calculate_derived_properties(norm_slice_df, norm_r_keys)
    return post_df


def flow_vars(avg_slice_df, u_keys, r_keys,
              norm_u_keys, norm_r_keys, u_reference):
    """Normalize velocity and Reynolds stress.

    Args:
        avg_slice_df (DataFrame): Averaged slice dataframe.
        norm_u_keys (list): Keys to assign to normalized velocity components.
        norm_r_keys (list): Keys to assign to normalized Reynolds stress tensor.
        u_reference (float): Reference velocity used for normalization.
    """
    dataframe = velocity(avg_slice_df,
                         u_keys,
                         norm_u_keys,
                         u_reference)
    dataframe = reynolds(dataframe,
                         r_keys,
                         norm_r_keys,
                         u_reference)
    return dataframe


def normalize_coordinates(avg_slice_df, coord_keys,
                          norm_coord_keys, length_ref):
    """Normalize the coordinates by a reference length.

    Args:
        avg_slice_df (DataFrame): Averaged slice dataframe.
        norm_coord_keys (list): Keys to assign to normalized coordinate components.
        length_ref (float): Reference length used for normalization.
    """
    dataframe = avg_slice_df.copy()
    dataframe[norm_coord_keys] = dataframe[coord_keys]/length_ref
    return dataframe


def velocity(avg_slice_df, u_keys, norm_u_keys, u_reference):
    """Normalize the flow velocity vector by a reference velocity.

    Args:
        avg_slice_df (DataFrame): Averaged slice dataframe.
        norm_u_keys (list): Keys to assign to normalized velocity components.
        u_reference (float): Reference velocity used for normalization.
    """
    dataframe = avg_slice_df.copy()
    dataframe[norm_u_keys] = dataframe[u_keys]/u_reference
    return dataframe


def reynolds(avg_slice_df, r_keys, norm_r_keys, u_reference):
    """Normalize the Reynolds stress tensor.

    Args:
        avg_slice_df (DataFrame): Averaged slice dataframe.
        norm_r_keys (list): Keys to assign to normalized Reynolds stress tensor.
        u_reference (float): Reference velocity used for normalization.
    """
    dataframe = avg_slice_df.copy()
    dataframe[norm_r_keys] = dataframe[r_keys]/(u_reference**2)
    return dataframe


def calculate_derived_properties(slice_df, r_keys):
    """R keys in the order of `SymmetricTensorStack` components,
    i.e. ("ii", "jj", "kk", "ij", "jk", "ik")."""
    symm_tensor_array = slice_df[r_keys].to_numpy()
    reynolds_stress = symmetric_tensor_array_to_tensor_stack(symm_tensor_array)
    tke = calculate_tke(reynolds_stress)
    anistropy_tensor = calculate_anisotropy_tensor(reynolds_stress)
    second_invariant = calculate_second_invariant(anistropy_tensor)*(-1)
    third_invariant = calculate_third_invariant(anistropy_tensor)
    df = slice_df.copy()
    derived_properties_keys = ["k/U_inf^2", "-II", "III"]
    derived_properties_arrays = [tke, second_invariant, third_invariant]
    for key, array in zip(derived_properties_keys, derived_properties_arrays):
        df[key] = array
    return df


def symmetric_tensor_array_to_tensor_stack(symm_tensor_array):
    return dt.SymmetricTensorStack(symm_tensor_array).to_array()


def calculate_tke(tensor):
    return 1/2*np.trace(tensor, axis1=1, axis2=2)


def calculate_anisotropy_tensor(tensor):
    tke = calculate_tke(tensor)+10**-7
    return tensor/(2*tke.reshape(-1, 1, 1)) - np.identity(3)/3


def calculate_second_invariant(tensor):
    a2 = np.matmul(tensor, tensor)
    trace_squared = np.trace(tensor, axis1=1, axis2=2)**2
    trace_of_square = np.trace(a2, axis1=1, axis2=2)
    return 1/2*(trace_squared - trace_of_square)


def calculate_third_invariant(anisotropy_tensor):
    return np.linalg.det(anisotropy_tensor)
