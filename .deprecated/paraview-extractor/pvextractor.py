import json
import os
import glob
import time


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--openfoam-source",
                              help="Flag if reading openfoam case",
                              action="store_true",)
    source_group.add_argument("--csv-source",
                              help="Flag if reading csv file",
                              action="store_true")
    parser.add_argument("--vtk-source",
                        help="Flag if reading vtk file",
                        action="store_true")

    parser.add_argument("--x-col",
                        help="Column to use as X coordinate if reading "
                             "from csv.",
                        default="x")
    parser.add_argument("--y-col",
                        help="Column to use as Y coordinate if reading "
                             "from csv.",
                        default="y")
    parser.add_argument("--z-col",
                        help="Column to use as Z coordinate if reading "
                             "from csv.",
                        default="z")
    parser.add_argument("--path-to-source", "-p",
                        help="Path pointing to the source file.",
                        default=None)
    parser.add_argument("--config-file", help="Path to configuration file.",
                        default=None)
    parser.add_argument("--output-dir",
                        help="Path to directory to dump files in.",
                        default="./raw/")
    return parser.parse_args()


def go_to_timestep(timestep):
    from paraview.simple import GetAnimationScene
    scene = GetAnimationScene()
    if timestep == "latest":
        scene.GoToLast()
        return
    scene.AnimationTime = timestep


def activate_cell_arrays(input_source, variables: list):
    input_source.CellArrays = variables
    return input_source


def extract_line(input_data, point1, point2, resolution, timestep, variables,
                 plot_over_line=None):
    from paraview.simple import PlotOverLine
    go_to_timestep(timestep)
    try:
        activate_cell_arrays(input_data, variables)
    except AttributeError:
        print("Can't activate specified cell arrays, will extract everything.")
    if plot_over_line is None:
        plot_over_line = PlotOverLine(registrationName="ExtractedLine",
                                      Input=input_data, Source="Line")
    plot_over_line.Source.Point1 = point1
    plot_over_line.Source.Point2 = point2
    plot_over_line.Source.Resolution = resolution
    return plot_over_line


def create_spreadsheet_view(source):
    from paraview.simple import CreateView, Show, AssignViewToLayout
    spreadsheet_view = CreateView('SpreadSheetView')
    source_display = Show(source, spreadsheet_view,
                          'SpreadSheetRepresentation')
    AssignViewToLayout(view=spreadsheet_view)
    return spreadsheet_view


def export_spreadheet_view_as_csv(csv_file, spreadsheet_view):
    from paraview.simple import ExportView
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    ExportView(csv_file, spreadsheet_view)


def read_config(config_json=None, **kwargs):
    with open(config_json, "r") as f:
        return json.load(f, **kwargs)


def read_openfoam_case(source_file):
    from paraview.simple import OpenFOAMReader
    print(f"Reading OpenFOAM source from {source_file}")
    case_source = OpenFOAMReader(registrationName='foam',
                                 FileName=source_file)
    case_source.MeshRegions = ["internalMesh"]
    return case_source


def read_csv_source(source_file,
                    x_col,
                    y_col,
                    z_col="",
                    two_dimensional=True):
    from paraview.simple import (CSVReader,
                                 TableToPoints,
                                 Delaunay2D,
                                 Delaunay3D)
    csv_source = CSVReader(registrationName="csv", FileName=source_file)
    table_to_points = TableToPoints(registrationName="points",
                                    Input=csv_source)
    table_to_points.XColumn = x_col
    table_to_points.YColumn = y_col
    if two_dimensional:
        table_to_points.a2DPoints = 1
        return Delaunay2D(registrationName="surface", Input=table_to_points)
    table_to_points.ZColumn = z_col
    return Delaunay3D(registrationName="volume", Input=table_to_points)


def read_vtk_source(source_file, registration_name=None):
    from paraview.simple import LegacyVTKReader
    if registration_name is None:
        registration_name = source_file
    return LegacyVTKReader(registrationName=registration_name,
                           FileNames=[source_file])


def extract_plane(input_data, origin, point1, point2,
                  x_res, y_res, timestep, variables, plane=None):
    from paraview.simple import Plane, ResampleWithDataset
    go_to_timestep(timestep)
    activate_cell_arrays(input_data, variables)
    if plane is None:
        plane = Plane(registrationName="plane")
    plane.Origin = origin
    plane.Point1 = point1
    plane.Point2 = point2
    plane.XResolution = x_res
    plane.YResolution = y_res
    resample_with_dataset = ResampleWithDataset(registrationName="PlaneSample",
                                                SourceDataArrays=input_data,
                                                DestinationMesh=plane)
    return plane, resample_with_dataset


def extract_and_export_plane(input_data, plane_definition, plane=None,
                             output_dir="."):
    origin = plane_definition["origin"]
    point1 = plane_definition["point1"]
    point2 = plane_definition["point2"]
    x_res = plane_definition["x_res"]
    y_res = plane_definition["y_res"]
    timestep = plane_definition["timestep"]
    variables = plane_definition["variables"]
    plane_source, resample_with_dataset = extract_plane(input_data, origin,
                                                        point1, point2, x_res,
                                                        y_res, timestep,
                                                        variables, plane)
    spreadsheet_view = create_spreadsheet_view(resample_with_dataset)
    output_file = plane_definition["output"]
    output_file = os.path.join(output_dir, output_file)
    export_spreadheet_view_as_csv(output_file, spreadsheet_view)
    delete_view(spreadsheet_view)
    return plane_source


def extract_and_export_planes(input_data, planes_to_extract, output_dir="."):
    plane = None
    for plane_definition in planes_to_extract:
        plane = extract_and_export_plane(input_data, plane_definition, plane,
                                         output_dir)


def extract_and_export_line(input_data, line_definition, line=None,
                            output_dir="."):
    point1 = line_definition["point1"]
    point2 = line_definition["point2"]
    resolution = line_definition["resolution"]
    timestep = line_definition["timestep"]
    variables = line_definition["variables"]
    line = extract_line(input_data, point1, point2,
                        resolution, timestep, variables, line)
    spreadsheet_view = create_spreadsheet_view(line)
    output = line_definition["output"]
    output = os.path.join(output_dir, output)
    export_spreadheet_view_as_csv(output, spreadsheet_view)
    delete_view(spreadsheet_view)
    return line


def extract_and_export_lines(input_data, lines_to_extract, output_dir="."):
    line = None
    for line_definition in lines_to_extract:
        line = extract_and_export_line(input_data, line_definition, line,
                                       output_dir)


def delete_view(view):
    from paraview.simple import Delete
    Delete(view)


def main():
    args = parse_args()
    config = read_config(args.config_file)
    planes_to_extract = config.pop("planes", [])
    lines_to_extract = config.pop("lines", [])
    start_time = time.perf_counter()
    print("Loading data")
    if args.openfoam_source:
        source = read_openfoam_case(args.path_to_source)
    elif args.csv_source:
        source = read_csv_source(args.path_to_source,
                                 x_col=args.x_col,
                                 y_col=args.y_col,
                                 z_col=args.z_col)
    elif args.vtk_source:
        source = read_vtk_source(args.path_to_source)
    else:
        raise ValueError("Please specify type of source.")
    loaded_time = time.perf_counter()
    print(f"Data loaded. Time taken: {loaded_time - start_time:.2f} s")
    extract_and_export_planes(source, planes_to_extract,
                              output_dir=args.output_dir)
    exported_planes_time = time.perf_counter()
    print(f"{len(planes_to_extract)} planes extracted. Time taken: "
          f"{exported_planes_time - loaded_time:.2f} s")
    extract_and_export_lines(source, lines_to_extract,
                             output_dir=args.output_dir)
    exported_lines_time = time.perf_counter()
    print(f"{len(lines_to_extract)} lines extracted. Time taken: "
          f"{exported_lines_time - exported_planes_time:.2f} s")
    print(f"Extraction finished. \n"
          f"Total time: {time.perf_counter() - start_time:.2f} s")


if __name__ == "__main__":
    main()
