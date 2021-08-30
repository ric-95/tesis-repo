from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class SourceConfig(ABC):

    @abstractmethod
    def cmd_options(self):
        pass


@dataclass
class OpenFOAMSourceConfig(SourceConfig):
    case_path: str

    def cmd_options(self):
        return f"--openfoam-source -p {self.case_path}"


@dataclass
class CSVSourceConfig(SourceConfig):
    csv_file: str
    x_col: str
    y_col: str
    z_col: str

    def cmd_options(self):
        return (f"--csv-source -p {self.csv_file} "
                f"--x-col {self.x_col} --y-col {self.y_col} "
                f"--z-col {self.z_col}")


@dataclass
class VTKSourceConfig(SourceConfig):
    vtk_file: str

    def cmd_options(self):
        return f"--vtk-source -p {self.vtk_file}"
