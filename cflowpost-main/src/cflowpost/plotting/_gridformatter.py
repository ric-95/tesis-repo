from ._baseformatter import (PropertyFormatter,
                                           FormattingPolicy)
from typing import Any, Mapping
from dataclasses import dataclass
from string import Template


class GridFormatter(PropertyFormatter):
    @classmethod
    def dashed_minor(cls,):
        major_kwargs = dict(axis="both",
                            linewidth=0.75,
                            )
        minor_kwargs = dict(axis="both",
                            linestyle="--",
                            linewidth=0.35,
                            )
        dashed_minor_policy = GridFormattingPolicy(axis="both",
                                                   major_kwargs=major_kwargs,
                                                   minor_kwargs=minor_kwargs,
                                                   )
        return cls(policy=dashed_minor_policy)


@dataclass
class GridFormattingPolicy(FormattingPolicy):
    which: str = "major"
    axis: str = "both"
    major_kwargs: Mapping[str, Any] = None
    minor_kwargs: Mapping[str, Any] = None

    def __post_init__(self):
        valid_which = {"both", "major", "minor"}
        valid_axis = {"both", "x", "y"}
        fields = ("which", "axis")
        valid_inputs = (valid_which, valid_axis)
        self._check_if_fields_valid(fields, valid_inputs)
        if self.major_kwargs is None:
            self.major_kwargs = dict()
        if self.minor_kwargs is None:
            self.minor_kwargs = dict()

    def apply(self, ax):
        ax.grid(which=self.which)
        if self.major_kwargs:
            ax.grid(which="major", **self.major_kwargs)
        if self.minor_kwargs:
            ax.grid(which="minor", **self.minor_kwargs)
        return ax
