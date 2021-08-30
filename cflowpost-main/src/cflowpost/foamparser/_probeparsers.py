import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class OpenFOAMProbeParser(ABC):
    """Abstract base class for parsing OpenFOAM probe files.
    Below is an example of a vector probe file produced by OpenFOAM.

    The probes are detailed at the beginning of the probe file.

    These are commented out by '#' characters.

    The probe data is formatted into a table and it looks like this:

    ```
    # Probe 0 (0 0 0.06)
    # Probe 1 (0 0 0.1)
    # Probe 2 (0 0.0305 -0.006)
    # Probe 3 (0 0.0305 0.006)
    # Probe 4 (0 0.06 0)
    #       Probe             0             1             2             3             4
    #        Time
    0.000103526             (-0.00244073 -0.00542589 2.21129)             (-0.00307846 0.00497887 1.35113)             (0.00111016 -0.0322428 7.80445)             (0.0744061 -2.2916 4.16031)             (-0.11998 1.81382 5.9705)
    0.000203003             (-0.0022293 -0.00449709 2.22242)             (-0.0030485 0.00505502 1.35891)             (0.00241385 -0.0312633 7.81685)             (0.0751307 -2.37652 4.19252)             (-0.120717 1.81705 6.00923)
    0.000305047             (-0.00204538 -0.0036662 2.23392)             (-0.00304933 0.00511356 1.36711)             (0.00318765 -0.0303157 7.82468)             (0.0754719 -2.47068 4.23277)             (-0.121444 1.82007 6.05034)
    ```
    """

    @abstractmethod
    def parse_probe_to_dfs(self, probe_contents):
        pass

    def _count_probes(self, probe_contents):
        """Counts the probes present in the probe file.

        Notice that the last two commented lines correspond to the
        table headers.

        Thus, the total probes can be obtained by counting the first
        '#' characters and subtracting 2."""
        header_lines = self._get_header_lines(probe_contents)
        total_header_lines = len(header_lines)
        return total_header_lines - 2

    @staticmethod
    def _get_header_lines(probe_contents):
        return list(filter(lambda line: "#" == line[0],
                           probe_contents.splitlines()))

    def _get_probe_positions(self, probe_contents):
        positions = {}
        header_lines = self._get_header_lines(probe_contents)
        for probe_number, line in enumerate(header_lines):
            if '(' in line:
                probe_position = self._get_probe_position(line)
                positions[probe_number] = probe_position
            else:
                break
        return positions

    @staticmethod
    def _get_probe_position(line):
        pos_start_index = line.find('(')
        pos_end_index = line.find(')')
        return line[pos_start_index:pos_end_index + 1]

    @staticmethod
    def _format_probe_into_lines(probe_contents):
        probe_contents = probe_contents.rstrip('\n')
        return probe_contents.splitlines()


class OpenFOAMScalarProbeParser(OpenFOAMProbeParser):

    def parse_probe_to_dfs(self, probe_contents):
        raise NotImplementedError


class OpenFOAMVectorProbeParser(OpenFOAMProbeParser):
    """
    This class should parse a vector probe file into a
    MultiIndex DataFrame.

    It inherits from the `ProbeParser` class, which serves as the base
    for the parser of either scalar, vectorial or tensorial quantities.
    """

    def parse_probe_to_dfs(self, probe_contents):
        probe_lines = self._format_probe_into_lines(probe_contents)
        probe_count = self._count_probes(probe_contents)
        probe_positions = self._get_probe_positions(probe_contents)
        datapoints_list = self.__extract_datapoints(probe_lines, probe_count)
        nested_u_dict = self.__get_u_dictionary(datapoints_list, probe_count)
        return self.__get_u_dataframes(nested_u_dict), probe_positions

    def __get_u_dictionary(self, datapoints_list, probe_count):
        # This method returns a nested dictionary containing the velocity
        # components of each probe.
        # Each inner dictionary will be used to construct a dataframe
        u_dict = {}
        for i in range(probe_count):
            u_dict[f'U_{i}'] = {'Time': [], 'Ux': [], 'Uy': [], 'Uz': []}
            ui_dict = u_dict[f'U_{i}']
            for data_point in datapoints_list:
                timepoint = float(data_point[0])
                ui_dict['Time'].append(timepoint)
                u = self.convert_openfoam_vector_to_array(data_point[i + 1])
                u_dict[f'U_{i}'] = self.add_vector_to_comps_dict(u, ui_dict)
        return u_dict

    @staticmethod
    def __get_u_dataframes(nested_u_dict):
        """Returns a dictionary of dataframes.

        Each key represents a velocity component.

        Each dataframe contains the transient data for one velocity component.

        The dataframes correspond to ONLY ONE PROBE DATASET."""
        return {f"U_{i}": pd.DataFrame(nested_u_dict[u_probe])
                for i, u_probe in enumerate(nested_u_dict)}

    def __extract_datapoints(self, probe_lines, probe_count):
        probe_lines = [line.strip() for line in probe_lines]
        data_points_list = [self.__extract_datapoint(line, probe_count)
                            for line in probe_lines if "#" not in line]
        return data_points_list

    @staticmethod
    def __extract_datapoint(line: str, probe_count):
        """This method returns the data point associated to a single
        line in the form of a list.

        The length of this list depends upon the number of probes.

        Thus this method should work with any amount of probes."""

        "Get the index of the first blank space."
        time_index = line.find(' ')

        "The time instant is contained from the first character until the first space"
        time_point = line[0:time_index]

        "Initialize a list for the data points"
        data_points = []

        "The data points should be searched starting from the first blank space"
        data_point_start_search = time_index

        for _ in range(probe_count):
            "Each vector is contained in between parentheses"
            "Find the first '(' after the start_search index"
            data_point_start_index = line.find('(', data_point_start_search)

            "Find the closing parenthesis"
            data_point_end_index = line.find(')', data_point_start_search + 1)

            "Slice the vector contained between the found parentheses"
            data_point = line[data_point_start_index:data_point_end_index + 1]

            "Append the data point to the list"
            data_points.append(data_point)
            "Update the start_search index for the next loop"
            data_point_start_search = data_point_end_index
        "Create a list which will serve as the row in the DataFrame"
        data_string_list = [time_point, *data_points]
        return data_string_list

    @staticmethod
    def parse_vector():
        pass

    @staticmethod
    # This function returns an array of vector components in float
    # Its output is the input of the add_vector_to_comps_dict
    def convert_openfoam_vector_to_array(of_vector_str):
        of_vector_str = of_vector_str.strip('()')
        of_vector_comps = of_vector_str.split(' ')
        counter = 0
        for comp in of_vector_comps:
            of_vector_comps[counter] = float(comp)
            counter += 1
        return np.array(of_vector_comps)

    @staticmethod
    def add_vector_to_comps_dict(vector, comp_dict):
        comp_dict['Ux'].append(vector[0])
        comp_dict['Uy'].append(vector[1])
        comp_dict['Uz'].append(vector[2])
        return comp_dict
