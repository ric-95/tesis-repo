from dataclasses import dataclass, field
from ._extractionconfig import ExtractionConfig
from ._sourceconfig import SourceConfig
from typing import Any

PVBATCH_DEFAULT_PATH = ("/home/ricardo/ParaView-5.9.1-MPI-Linux-Python3.8-64bit"
                        "/bin/pvbatch")


@dataclass
class PVXConfig:
    extraction_config: ExtractionConfig
    source_config: SourceConfig
    pvx_bin: str
    pvbatch_bin: str = field(default=PVBATCH_DEFAULT_PATH)
    extraction_config_file: Any = field(repr=False, default=None)

    def command_string(self, output_dir):
        source_options = self.source_config.cmd_options()
        self.extraction_config_file = self.extraction_config.to_temp_file()
        config_fname = self.extraction_config_file.name
        return (f"{self.pvbatch_bin} {self.pvx_bin} {source_options} " 
                f"--output-dir {output_dir}"
                f" --config-file {config_fname}")
