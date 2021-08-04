def to_tecplot(df, var_list):
    try:
        import tecplot as tp
    except ImportError:
        print(f"Pytecplot package not installed.")
        exit()

    tp.session.connect()
    dataset = tp.active_frame().create_dataset("Data", var_list)
    shape = _get_2d_shape(df, "r", "z")
    numerical_zone = dataset.add_ordered_zone("Numerical", shape=shape)
    _export_variables_from_dataframe(df, var_list, numerical_zone)
    print("Finished exporting to tecplot.")


def _get_2d_shape(df, x_key, y_key) -> tuple:
    """Infer the shape of the original 2D slice.

    Args:
        df: DataFrame.
        x_key (str): Key for the x_direction in dataframe.
        y_key (str): Key for the y_direction in dataframe

    Returns:
        x_shape, y_shape (tuple)"""
    return df[x_key].nunique(), df[y_key].nunique()


def _add_var_to_zone(zone, var, values):
    print(f"Adding {var}")
    zone.values(var)[:] = values


def _get_variable_values(df, var):
    try:
        return df[var].to_numpy(), True
    except KeyError:
        return None, False


def _export_variables_from_dataframe(df, var_list, zone):
    for var in var_list:
        values, found = _get_variable_values(df, var)
        if not found:
            print(f"{var} missing. Skipped.")
            continue
        _add_var_to_zone(zone, var, values)
