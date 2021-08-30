from ._probeparsers import OpenFOAMVectorProbeParser


def _read_probe(probe_file):
    with open(probe_file) as f:
        return f.read()


def _parse_openfoam_probe_file_to_dataframe(probe_file, parser):
    probe_contents = _read_probe(probe_file)
    return parser.parse_probe_to_dfs(probe_contents)


def parse_openfoam_vectorprobe(probe_file):
    parser = OpenFOAMVectorProbeParser()
    return _parse_openfoam_probe_file_to_dataframe(probe_file, parser)
