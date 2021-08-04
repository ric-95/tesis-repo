"""Constructs the config file for the extraction of slices
to perform an azimuthal average.

Usage:
    python ./azimuthal_average_pipeline.py --num-planes 16 --timestep latest \\
    --point1 0.09 0 --point2 0 0.15 --x-res 90 --y-res 150 --output-dir "."

Assumptions:

    - Z is the axis of rotation
    - Origin lies at [0 0 0]
"""

import json
from string import Template
import numpy as np
import os

ORIGIN = (0, 0, 0)
PI = np.pi
VARIABLES = ("UMean", "UPrime2Mean", "pMean")
FILE_TEMPLATE = Template("azim_average/raw/SLICE${number}.csv")


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--num-planes", type=int, default=16,
                        help="Number of planes to average.")
    parser.add_argument("--timestep", default="latest",
                        help="Timestep at which to extract sample.",)
    parser.add_argument("--point1", nargs=2, type=float,
                        help="Radial and axial coordinates of first point of"
                             "plane. First value is the radial position, second"
                             "value is the axial position.")
    parser.add_argument("--point2", nargs=2, type=float,
                        help="Radial and axial coordinates of second point of"
                             "plane.First value is the radial position, second"
                             "value is the axial position.")
    parser.add_argument("--x-res", type=int, help="Resolution in x direction.")
    parser.add_argument("--y-res", type=int, help="Resolution in y direction.")
    parser.add_argument("--output-dir", type=str, help="Directory to write"
                                                       "json dump.")
    return parser.parse_args()


def create_plane_definition(origin, point1, point2, x_res, y_res,
                            timestep, variables, output):
    return {"origin": origin, "point1": point1,
            "point2": point2, "x_res": x_res,
            "y_res": y_res, "timestep": timestep,
            "variables": variables, "output": output}


def transform_cylindrical_to_cartesian(radial, axial, theta):
    """Assumes that axial direction coincides with the z-axis"""
    x = radial*np.cos(theta)
    y = radial*np.sin(theta)
    z = axial
    return [x, y, z]


def dump_to_json(obj, file, **kwargs):
    with open(file, "w") as f:
        f.write(json.dumps(obj, **kwargs))


def run(point1,
        point2,
        num_planes,
        x_res,
        y_res,
        timestep,
        output_dir):
    radial1, axial1 = point1
    radial2, axial2 = point2
    plane_nums = np.arange(num_planes)
    thetas = plane_nums*2*PI/num_planes
    point1s = [transform_cylindrical_to_cartesian(radial1, axial1, theta)
               for theta in thetas]
    point2s = [transform_cylindrical_to_cartesian(radial2, axial2, theta)
               for theta in thetas]
    outputs = [FILE_TEMPLATE.substitute(number=str(plane_num).zfill(3))
               for plane_num in plane_nums]
    plane_definitions = [create_plane_definition(ORIGIN, point1, point2,
                                                 x_res, y_res, timestep,
                                                 VARIABLES, output)
                         for point1, point2, output
                         in zip(point1s, point2s, outputs)]
    path = os.path.join(output_dir, "azimuthal-average-extraction.json")
    dump_to_json({"planes": plane_definitions}, path, indent=4)


def main():
    args = parse_args()
    run(args.point1, args.point2, args.num_planes,
        args.x_res, args.y_res, args.timestep, args.output_dir)


if __name__ == "__main__":
    main()
