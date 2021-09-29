"""Extracts a slice and lines from a 2-dimensional wedge case.

Usage:
    python ./extract_rans_data.py $case --timestep latest \\
    --radial-extension 0.09 --axial-extension 0.15 --x-res 90 --y-res 150 \\
    --output-dir "."

Assumes:
    - Axial direction is the Z axis.
"""
import json
import os
import argparse
import pandas as pd
from cflowpost import pvx
from cflowpost.processing import process_turbulent_flow_fields

U_REF = 11.8
LENGTH_REF = 0.06
VARIABLES_TO_EXTRACT = ("U", "turbulenceProperties:R", "p", "k")
PARAVIEW_COORD_KEYS = tuple(f"Points_{i}" for i in range(3))
COORD_KEYS = ("t", "r", "x")
NORM_COORD_KEYS = tuple(f"{coord}/D_b" for coord in COORD_KEYS)

PARAVIEW_U_KEYS = ("U_0", "U_1", "U_2")
U_KEYS = ("w", "v", "u")
NORM_U_KEYS = tuple(f"{u_key}/U_inf" for u_key in U_KEYS)

PARAVIEW_R_KEYS = tuple(f"turbulenceProperties:R_{i}" for i in range(6))
R_KEYS = ("R_tt",
          "R_rr",
          "R_zz",
          "R_rt",
          "R_rz",
          "R_tz")
NORM_R_KEYS = tuple(f"{r_key}/U_inf^2".replace("z", "x")
                    for r_key in R_KEYS)

OUTPUT_DIR = "pvx"
RAW_SLICE_FILE = "raw/raw_slice.csv"
PROCESSED_SLICE_FILE = "slice.csv"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases",
                        metavar="OPENFOAM RANS CASES",
                        nargs="+",
                        type=str)
    parser.add_argument("--radial-extension",
                        default=0.09,
                        type=float)
    parser.add_argument("--axial-extension",
                        default=0.15,
                        type=float)
    parser.add_argument("--x-res", type=int, default=90, )
    parser.add_argument("--y-res", type=int, default=150, )
    parser.add_argument("--timestep", default="latest", )
    return parser.parse_args()


def main():
    args = parse_args()
    r_max, x_max = args.radial_extension, args.axial_extension
    timestep = args.timestep
    if timestep != "latest":
        timestep = float(timestep)

    for case_dir in args.cases:
        run(case_dir=case_dir,
            timestep=timestep,
            r_max=r_max,
            x_max=x_max,
            x_res=args.x_res,
            y_res=args.y_res,)


def run(case_dir, timestep, r_max, x_max, x_res, y_res):
    """

    Parameters
    ----------
    case_dir : Path to OpenFOAM case
    timestep : Timestep to extract data from
    r_max : Radial extension from origin to extract
    x_max : Axial extension from origin to extract
    x_res : Resolution in the x direction relative to the plane
    y_res : Resolution in the y direction relative to the plane
    """
    raw_slice_csv = extract_raw_slice(case_dir=case_dir,
                                      r_max=r_max,
                                      x_max=x_max,
                                      x_res=x_res,
                                      y_res=y_res,
                                      timestep=timestep,
                                      variables=list(VARIABLES_TO_EXTRACT))
    raw_slice = pd.read_csv(raw_slice_csv)
    processed_slice = process_raw_slice(raw_slice)
    processed_slice_csv = os.path.join(case_dir, OUTPUT_DIR,
                                       PROCESSED_SLICE_FILE)
    processed_slice.to_csv(processed_slice_csv, index=False)
    extract_processed_lines(case_dir, processed_slice_csv, )
    return


def extract_raw_slice(case_dir, r_max, x_max, x_res,
                      y_res, timestep, variables, ):
    source_config = pvx.openfoam_source(case_dir)
    raw_slice_output = os.path.join(OUTPUT_DIR, RAW_SLICE_FILE)
    slice_extraction_config = build_slice_configuration_config(
        r_max, x_max, x_res=x_res, y_res=y_res,
        timestep=timestep, variables=variables, output=raw_slice_output)
    pvx.extract(source_config=source_config,
                extraction_config=slice_extraction_config,
                output_dir=case_dir)
    return os.path.join(case_dir, raw_slice_output)


def build_slice_configuration_config(r_max, x_max,
                                     x_res, y_res,
                                     variables,
                                     timestep="latest",
                                     output="./slice.csv"):
    origin = [0, 0, 0]
    point1 = [0, r_max, 0]
    point2 = [0, 0, x_max]
    plane_def = pvx.plane_definition(origin=origin,
                                     point1=point1,
                                     point2=point2,
                                     x_res=x_res,
                                     y_res=y_res,
                                     variables=variables,
                                     timestep=timestep,
                                     output=output)
    return pvx.build_extraction_config(plane_definitions=[plane_def])


def process_raw_slice(raw_slice, ):
    df = raw_slice.copy()
    for coord_key, pv_coord_key in zip(COORD_KEYS, PARAVIEW_COORD_KEYS):
        df[coord_key] = df[pv_coord_key]
    processed_slice = process_turbulent_flow_fields(
        df, length_ref=LENGTH_REF, u_ref=U_REF,
        coord_keys=COORD_KEYS, norm_coord_keys=NORM_COORD_KEYS,
        u_keys=PARAVIEW_U_KEYS, norm_u_keys=NORM_U_KEYS,
        r_keys=PARAVIEW_R_KEYS, norm_r_keys=NORM_R_KEYS)
    return processed_slice


def extract_processed_lines(case_dir,
                            slice_csv,
                            x_col="r/D_b",
                            y_col="x/D_b",
                            z_col="t"):
    dir_ = os.path.dirname(__file__)
    line_config_path = os.path.join(dir_, "line_extraction_config.json")
    line_extraction_config = build_line_configuration_config(line_config_path)
    csv_source = pvx.csv_source(slice_csv, x_col=x_col,
                                y_col=y_col, z_col=z_col)
    output_dir = os.path.join(case_dir, OUTPUT_DIR)
    pvx.extract(extraction_config=line_extraction_config,
                source_config=csv_source,
                output_dir=output_dir)
    return


def build_line_configuration_config(config_file):
    with open(config_file, mode="r") as f:
        config_json = json.loads(f.read())
    return pvx.extraction_json_to_config(config_json)


if __name__ == "__main__":
    main()
