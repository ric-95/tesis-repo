import json
import os
import glob
import time


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--openfoam-case-dir", "-c",
                        help="Directory containing openfoam case", default=".")
    parser.add_argument("--config-file", help="Path to configuration file.")
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
    activate_cell_arrays(input_data, variables)
    if plot_over_line is None:
        plot_over_line = PlotOverLine(registrationName="ExtractedLine",
                                      Input=input_data, Source="Line")
    plot_over_line.Source.Point1 = point1
    plot_over_line.Source.Point2 = point2
    plot_over_line.Source.Resolution = resolution
    return plot_over_line


def extract_plane(input_data, origin, point1, point2,
                  x_res, y_res, timestep, variables, plane=None):
    from paraview.simple import Plane, ResampleWithDataset
    go_to_timestep(timestep)
    activate_cell_arrays(input_data, variables)
    plane_source = plane
    if plane is None:
        plane_source = Plane(registrationName="plane")
    plane_source.Origin = origin
    plane_source.Point1 = point1
    plane_source.Point2 = point2
    plane_source.XResolution = x_res
    plane_source.YResolution = y_res
    resample_with_dataset = ResampleWithDataset(registrationName="PlaneSample",
                                                SourceDataArrays=input_data,
                                                DestinationMesh=plane_source)
    return plane_source, resample_with_dataset


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


def read_config(config_json, **kwargs):
    with open(config_json, "r") as f:
        return json.load(f, **kwargs)


def read_openfoam_case(case_dir):
    from paraview.simple import OpenFOAMReader
    file_name = os.path.join(case_dir, "system/controlDict")
    print(f"Reading OpenFOAM source from {file_name}")
    case_source = OpenFOAMReader(registrationName='controlDict',
                                 FileName=file_name)
    case_source.MeshRegions = ["internalMesh"]
    return case_source


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
    print("Loading OpenFOAM data")
    openfoam_source = read_openfoam_case(args.openfoam_case_dir)
    loaded_time = time.perf_counter()
    print(f"Data loaded. Time taken: {loaded_time - start_time:.2f} s")
    extract_and_export_planes(openfoam_source, planes_to_extract,
                              output_dir=args.openfoam_case_dir)
    exported_planes_time = time.perf_counter()
    print(f"Planes extracted. Time taken: "
          f"{exported_planes_time - loaded_time:.2f} s")
    extract_and_export_lines(openfoam_source, lines_to_extract,
                             output_dir=args.openfoam_case_dir)
    exported_lines_time = time.perf_counter()
    print(f"Lines extracted. Time taken: "
          f"{exported_lines_time - exported_planes_time:.2f} s")
    print(f"Extraction finished. \n"
          f"Total time: {time.perf_counter() - start_time:.2f} s")


if __name__ == "__main__":
    main()
