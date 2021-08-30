from dataclasses import dataclass, asdict
from ._definitions import Line, Plane, Streamlines
from typing import List
from tempfile import NamedTemporaryFile
import json


@dataclass
class ExtractionConfig:
    planes: List[Plane] = None
    lines: List[Line] = None
    streamlines: List[Streamlines] = None

    def to_dict(self):
        return asdict(self)

    def to_temp_file(self, **kwargs):
        temp_file = NamedTemporaryFile(mode="w+", **kwargs)
        temp_file.write(json.dumps(self.to_dict()))
        temp_file.flush()
        return temp_file
