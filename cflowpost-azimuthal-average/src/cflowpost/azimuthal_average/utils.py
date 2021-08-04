import os


def cylindrical_vec_coords():
    return ["r", "t", "z"]


def cartesian_vec_coords():
    return ["x", "y", "z"]


def umean_cyl_coods():
    return [f"u_mean_{coord}" for coord in cylindrical_vec_coords()]


def umean_cart_coors():
    return [f"u_mean_{coord}" for coord in cartesian_vec_coords()]


def paraview_cart_coords():
    return [f"Points_{i}" for i in range(3)]


def umean_paraview_cart_coords():
    return [f"UMean_{i}" for i in range(3)]


def r_stress_paraview_cart_coords():
    return [f"UPrime2Mean_{i}" for i in range(6)]


def r_stress_cyl_coords():
    return ["R_rr", "R_rt", "R_rz", "R_tt", "R_tz", "R_zz"]


def normalized_r_stress_cyl_coords():
    return ["R<sub>rr</sub>/U<sub>∞</sub><sup>2</sup>",
            "R<sub>rt</sub>/U<sub>∞</sub><sup>2</sup>",
            "R<sub>rx</sub>/U<sub>∞</sub><sup>2</sup>",
            "R<sub>tt</sub>/U<sub>∞</sub><sup>2</sup>",
            "R<sub>xt</sub>/U<sub>∞</sub><sup>2</sup>",
            "R<sub>xx</sub>/U<sub>∞</sub><sup>2</sup>"]


def normalized_cyl_coords():
    return ["r/D<sub>b</sub>",
            "x/D<sub>b</sub>"]


def normalized_u_cyl_coords():
    return ["v/U<sub>∞</sub>",
            "w/U<sub>∞</sub>",
            "u/U<sub>∞</sub>"]


def derived_properties():
    return ["k/U<sub>∞</sub><sup>2</sup>", "-II", "III"]


def scalar_variables():
    return ["DESRegionMean",
            "DESRegionPrime2Mean",
            "kMean",
            "nutMean",
            "pMean",
            "pPrime2Mean"]


def tecplot_variables():
    return [*normalized_cyl_coords(),
            *normalized_u_cyl_coords(),
            *normalized_r_stress_cyl_coords(),
            *derived_properties(),
            *scalar_variables()]
