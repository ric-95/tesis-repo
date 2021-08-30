from ._extractionconfig import ExtractionConfig
from ._sourceconfig import (SourceConfig,
                            CSVSourceConfig,
                            OpenFOAMSourceConfig,
                            VTKSourceConfig)
from ._pvxconfig import PVXConfig
from ._definitions import Line, Plane
from typing import List
import json as _json


def build_config(line_definitions: List[Line] = None,
                 plane_definitions: List[Plane] = None):
    if line_definitions is None:
        line_definitions = []
    if plane_definitions is None:
        plane_definitions = []
    return ExtractionConfig(planes=plane_definitions, lines=line_definitions)


def dump_config(config: ExtractionConfig, file_obj, **kwargs):
    file_obj.write(_json.dumps(config.to_dict(), **kwargs))
    return
