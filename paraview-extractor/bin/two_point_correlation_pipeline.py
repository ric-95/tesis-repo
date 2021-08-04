import json
from string import Template
import numpy as np
import os


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--num-lines-per-sample", type=int, default=16,
                        help="Number of lines to extract per sample.")
    parser.add_argument("--timesteps-to-sample", nargs="+", type=float,
                        help="Timesteps at which to extract samples.")
    parser.add_argument("--point1", nargs=2, type=float,
                        help="Radial and axial coordinates of first point of"
                             "line. First value is the radial position, second"
                             "value is the axial position.")
    parser.add_argument("--point2", nargs=2, type=float,
                        help="Radial and axial coordinates of second point of"
                             "line.First value is the radial position, second"
                             "value is the axial position.")
    parser.add_argument("--line-resolution", type=int, help="Resolution of "
                                                            "extracted lines.")
    parser.add_argument("-o", type=str, help="Output file.",
                        default="tpcorr.json")
    return parser.parse_args()


FILE_TEMPLATE = Template("two_point_corr/r1=${r1}x1=${x1};r2=${r2}x2=${x2}"
                         "/raw/T=${timestep}_LINE${number}.csv")
VARIABLES = ("U", "UMean")
PI = np.pi


def create_line_definition(point1, point2, resolution, timestep, variables,
                           output):
    return {"point1": point1, "point2": point2,
            "resolution": resolution, "timestep": timestep,
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


def run(point1, point2, lines_per_timestep,
        line_resolution, timesteps, output_file):
    radial1, axial1 = point1
    radial2, axial2 = point2
    thetas = np.arange(lines_per_timestep) * 2 * PI / lines_per_timestep
    point1s = [transform_cylindrical_to_cartesian(radial1, axial1, theta)
               for theta in thetas]
    point2s = [transform_cylindrical_to_cartesian(radial2, axial2, theta)
               for theta in thetas]
    outputs_list = [[FILE_TEMPLATE.substitute(number=str(line_num).zfill(3),
                                              r1=radial1, x1=axial1,
                                              r2=radial2, x2=axial2,
                                              timestep=timestep, )
                     for line_num in range(len(thetas))]
                    for timestep in timesteps]
    lines = [create_line_definition(point1, point2, line_resolution,
                                    timestep, VARIABLES, output)
             for timestep, outputs in zip(timesteps,
                                          outputs_list)
             for point1, point2, output in zip(point1s, point2s, outputs)
             ]
    dump_to_json({"lines": lines}, output_file, indent=4)


def main():
    args = parse_args()
    run(args.point1, args.point2, args.num_lines_per_sample,
        args.line_resolution, args.timesteps_to_sample, args.o)


if __name__ == "__main__":
    main()
