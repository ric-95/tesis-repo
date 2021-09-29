from . import configbuilder
from ._definitions import Point, Line, Plane
import os
from typing import List, Union

PVBATCH_DEFAULT_PATH = os.environ.get("PVBATCH_BIN")


def extract(extraction_config: configbuilder.ExtractionConfig,
            source_config: configbuilder.SourceConfig,
            output_dir,
            pvbatch_bin=PVBATCH_DEFAULT_PATH):
    """Given an extraction and source configuration, use the provided `pvbatch`
    binary to extract data."""
    pvx_dir = os.path.dirname(__file__)
    pvx_bin = os.path.join(pvx_dir, "_extraction.py")
    pvxconfig = configbuilder.PVXConfig(extraction_config=extraction_config,
                                        source_config=source_config,
                                        pvx_bin=pvx_bin,
                                        pvbatch_bin=pvbatch_bin)
    cmd = pvxconfig.command_string(output_dir=output_dir)
    print("Calling process with command:")
    print(cmd)
    import subprocess
    result = subprocess.run(cmd, shell=True)
    return result


def vtk_source(vtk_file, ):
    return configbuilder.VTKSourceConfig(vtk_file=vtk_file)


def csv_source(csv_file, x_col, y_col, z_col):
    return configbuilder.CSVSourceConfig(csv_file=csv_file,
                                         x_col=x_col,
                                         y_col=y_col,
                                         z_col=z_col)


def openfoam_source(case_path):
    return configbuilder.OpenFOAMSourceConfig(case_path=case_path)


def line_definition(point1: Point, point2: Point,
                    resolution: int, timestep: float,
                    variables: List[str], output: str):
    return Line(point1=point1, point2=point2, resolution=resolution,
                timestep=timestep, variables=variables, output=output)


def plane_definition(origin: Point, point1: Point, point2: Point,
                     x_res: int, y_res: int, timestep: Union[float, str],
                     variables: List[str], output: str):
    return Plane(origin=origin, point1=point1, point2=point2,
                 x_res=x_res, y_res=y_res, timestep=timestep,
                 variables=variables, output=output)


def build_extraction_config(line_definitions: List[Line] = None,
                            plane_definitions: List[Plane] = None):
    if line_definitions is None:
        line_definitions = []
    if plane_definitions is None:
        plane_definitions = []
    return configbuilder.ExtractionConfig(planes=plane_definitions,
                                          lines=line_definitions)


def extraction_json_to_config(config_json, lines_key="lines",
                              planes_key="planes"):
    config_json["lines"] = [line_definition(**line_def)
                            for line_def in config_json[lines_key]]
    config_json["planes"] = [plane_definition(**plane_def)
                             for plane_def in config_json[planes_key]]
    return build_extraction_config(line_definitions=config_json[lines_key],
                                   plane_definitions=config_json[planes_key])
