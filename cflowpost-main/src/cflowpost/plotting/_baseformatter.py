import string
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from string import Template
from typing import Sequence


@dataclass
class FormattingPolicy(ABC):
    def to_dict(self):
        return asdict(self)

    @staticmethod
    def _check_if_valid_field(field_input, valid_values, errmsg):
        if field_input not in valid_values:
            raise ValueError(errmsg)

    def _check_if_fields_valid(self, fields: Sequence[str], valid_input_sets):
        errtemplate = Template("Invalid ${field} given. "
                                "${input_} not in ${valid}")
        for field, valid_inputs in zip(fields, valid_input_sets):
            input_ = self.to_dict()[field]
            err = errtemplate.substitute(field=field,
                                         input_=input_,
                                         valid=valid_inputs)
            self._check_if_valid_field(input_, valid_inputs, err)

    @abstractmethod
    def apply(self, ax):
        pass


class PropertyFormatter(ABC):

    def __init__(self, policy: FormattingPolicy):
        self.policy = policy

    def format(self, ax):
        self.policy.apply(ax)
