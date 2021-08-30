from matplotlib import markers as _markers


FILLED_MARKERS = ("o",
                  "^",
                  "s",
                  "v",
                  "D",
                  "X",
                  "<",
                  ">")
UNFILLED_MARKERS = (".",
                    "x",
                    _markers.CARETDOWN,
                    _markers.CARETUP,
                    _markers.CARETLEFT,
                    _markers.CARETRIGHT)
_DENSELY_DASHDOTDOTTED = (0, (3, 1, 1, 1, 1, 1))
_DASHDOTDOTTED = (0, (3, 3, 1, 3, 1, 3))
_DENSELY_DASHED = (0, (5, 1))
_LOOSELY_DASHED = (0, (5, 10))
DEFAULT_LINESTYLES = ("solid",
                      "dashed",
                      "dashdot",
                      _DENSELY_DASHDOTDOTTED,
                      _DENSELY_DASHED,
                      _DASHDOTDOTTED,
                      _DENSELY_DASHED,
                      _LOOSELY_DASHED,)
DEFAULT_COLORS = ("tab:blue",
                  "tab:orange",
                  "tab:green",
                  "tab:red",
                  "tab:purple",
                  "tab:olive",
                  "tab:brown",
                  "tab:cyan",
                  "indianred",
                  "goldenrod",
                  "darkseagreen",
                  "firebrick",
                  "teal",
                  "sienna",)
DEFAULT_MARKERS = FILLED_MARKERS
