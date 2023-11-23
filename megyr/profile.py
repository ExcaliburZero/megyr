from typing import Any, Optional

import os.path

import pandas as pd


def read_num_profiles(filepath: str, column_length: int = 12) -> int:
    with open(filepath, "r") as f:
        first_part = f.readline()[:column_length]

        no_spaces = "".join(first_part.split(" "))

        return int(no_spaces)


def read_all_profile_attributes(
    logs_dir: str,
    num_profiles: int,
    profile_prefix: str = "profile",
    profile_suffix: str = ".data",
) -> pd.DataFrame:
    attributes = pd.DataFrame()
    for i in range(1, num_profiles + 1):
        name = profile_prefix + str(i) + profile_suffix
        filepath = os.path.join(logs_dir, name)

        attr = read_profile_file(filepath, read_data=False).attributes
        attr["profile"] = i

        attributes = pd.concat([attributes, attr])

    return attributes


def read_profile_file(
    filepath: str,
    attributes_start_row: int = 1,
    data_start_row: int = 5,
    read_data: bool = True,
) -> "MESAProfile":
    attributes = pd.read_fwf(filepath, skiprows=attributes_start_row, nrows=1)
    data = pd.read_fwf(filepath, skiprows=data_start_row) if read_data else None

    return MESAProfile(attributes, data)


class MESAProfile:
    def __init__(self, attributes: pd.DataFrame, data: Optional[pd.DataFrame]) -> None:
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
                + '" is not a valid attribute for this MESA profile.'
            )

    def has_attribute(self, attr: str) -> bool:
        return attr in list(self.attributes.columns.values)
