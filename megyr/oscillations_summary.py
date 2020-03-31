from typing import Any

import pandas as pd


def read_oscillations_summary_file(
    filepath: str,
    attributes_start_row: int = 2,
    data_start_row: int = 5,
    column_width: int = 25,
) -> "OscillationsSummary":
    num_attributes = get_num_attributes(filepath, attributes_start_row)

    attr_widths = [column_width for _ in range(0, num_attributes)]

    attributes = pd.read_fwf(
        filepath, skiprows=attributes_start_row, nrows=1, widths=attr_widths
    )
    data = pd.read_fwf(filepath, skiprows=data_start_row)

    return OscillationsSummary(attributes, data)


def get_num_attributes(filepath: str, attributes_start_row: int) -> int:
    with open(filepath) as f:
        for i, line in enumerate(f):
            if i == attributes_start_row - 1:
                return len(line.split())

    raise Exception(
        "Unable to find attributes column number line in oscillations summary file."
    )


class OscillationsSummary:
    def __init__(self, attributes: pd.DataFrame, data: pd.DataFrame) -> None:
        self.attributes = attributes
        self.data = data

    def __str__(self) -> str:
        return str(self.attributes) + "\n" + str(self.data)

    def get_attribute(self, attr: str) -> Any:
        if self.has_attribute(attr):
            return self.attributes[attr].iloc[0]
        else:
            raise KeyError(
                'Attribute "'
                + attr
                + '" is not a valid attribute for this oscillations summary.'
            )

    def has_attribute(self, attr: str) -> bool:
        return attr in list(self.attributes.columns.values)
