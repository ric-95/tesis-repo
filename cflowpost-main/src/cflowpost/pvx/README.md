`pvx`
=====

Subpackage for automating complex data extraction pipelines leveraging 
an existing [ParaView](https://www.paraview.org/) installation. 

Each extraction is performed by specifying two separate configurations:

- Extraction Configuration
  
  Specifies the geometries to extract and where to store the results.
  As of now `pvx` is capable of extracting lines and planes. The parameters
  needed for any of these geometries are directly correlated to those
  one would specify in ParaView.

- Source Configuration
  
  Specifies the data source to be fed to ParaView. As of now `pvx` is capable
  of reading OpenFOAM data, VTK data and 2-dimensional CSV data.

By keeping the what from the how separate, `pvx` allows one to extract data 
from many different sources while maintaining a reproducible and reliable 
extraction workflow.

Also, defining these configuration objects is extremely simple. Simple 
wrapper functions are implemented at the root of the package to:

- Define geometries
  - `pvx.plane_definition`
  - `pvx.line_definition`
  ```python
  def line_definition(point1: Point, point2: Point,
                      resolution: int, timestep: float,
                      variables: List[str], output: str)

  def plane_definition(origin: Point, point1: Point, point2: Point,
                       x_res: int, y_res: int, timestep: float,
                       variables: List[str], output: str)
  
- Set the extraction configuration
  - `pvx.build_extraction_config(line_definitions, plane_definitions)`
- Specify a source
  - `pvx.openfoam_source(case_path)`
  - `pvx.vtk_source(vtk_file)`
  - `pvx.csv_source(csv_file, x_col, y_col, z_col)`

This is particularly useful for Large Eddy Simulations in complex flows 
because of the reduction in computational time yielded by the averaging
the flow in a certain dimension. 

In the following example will be shown the script needed to extract planes
to perform an azimuthal average of an axisymmetric 3D turbulent flow.

### Example: Azimuthal Planes Extraction

```python
"""Extracts slices to perform an azimuthal average.

Usage:
    python ./extract_slices_for_averaging.py --num-planes 16 --timestep latest \\
    --point1 0.09 0 --point2 0 0.15 --x-res 90 --y-res 150 --output-dir "."

Assumptions:

    - Z is the axis of rotation
    - Origin lies at [0 0 0]
"""


import numpy as np

from cflowpost import pvx
from string import Template

ORIGIN = (0., 0., 0.)
PI = np.pi
VARIABLES = ("UMean", "UPrime2Mean", "pMean")
FILE_TEMPLATE = Template("azim_average/raw/SLICE${number}.csv")


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--case-dir", type=str, default=".",
                        help="Path to OpenFOAM case directory.")
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
    return parser.parse_args()


def main():
    args = parse_args()
    extraction_config = build_extraction_config(cyl_point1=args.point1,
                                                cyl_point2=args.point2,
                                                num_planes=args.num_planes,
                                                x_res=args.x_res,
                                                y_res=args.y_res,
                                                timestep=args.timestep)
    source_config = pvx.openfoam_source(args.case_dir)
    output_dir = args.case_dir
    pvx.extract(
        extraction_config=extraction_config,
        source_config=source_config,
        output_dir=output_dir)


def build_extraction_config(cyl_point1,
                            cyl_point2,
                            num_planes,
                            x_res,
                            y_res,
                            timestep,
                            origin=ORIGIN,
                            variables=VARIABLES):
    radial1, axial1 = cyl_point1
    radial2, axial2 = cyl_point2
    plane_nums = np.arange(num_planes)
    thetas = plane_nums*2*PI/num_planes
    point1s = [transform_cylindrical_to_cartesian(radial1, axial1, theta)
               for theta in thetas]
    point2s = [transform_cylindrical_to_cartesian(radial2, axial2, theta)
               for theta in thetas]
    outputs = [FILE_TEMPLATE.substitute(number=str(plane_num).zfill(3))
               for plane_num in plane_nums]
    plane_definitions = [pvx.plane_definition(list(origin), point1, point2,
                                              x_res, y_res, timestep,
                                              list(variables), output)
                         for point1, point2, output
                         in zip(point1s, point2s, outputs)]
    return pvx.build_extraction_config(plane_definitions=plane_definitions)


def transform_cylindrical_to_cartesian(radial, axial, theta):
    """Assumes that axial direction coincides with the z-axis"""
    x = radial*np.cos(theta)
    y = radial*np.sin(theta)
    z = axial
    return [x, y, z]


if __name__ == "__main__":
    main()

```
