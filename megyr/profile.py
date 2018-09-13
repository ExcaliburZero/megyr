import os.path

import pandas as pd

def read_num_profiles(filepath, column_length=12):
    with open(filepath, "r") as f:
        first_part = f.readline()[:column_length]

        no_spaces = "".join(first_part.split(" "))

        return int(no_spaces)

def read_all_profile_attributes(logs_dir, num_profiles, profile_prefix="profile", profile_suffix=".data"):
    attributes = pd.DataFrame()
    for i in range(1, num_profiles + 1):
        name = profile_prefix + str(i) + profile_suffix
        filepath = os.path.join(logs_dir, name)

        attr = read_profile_file(filepath, read_data=False).attributes
        attr["profile"] = i

        attributes = pd.concat([attributes, attr])

    return attributes

def read_profile_file(filepath, attributes_start_row=1, data_start_row=5, read_data=True):
    attributes = pd.read_fwf(filepath, skiprows=attributes_start_row, nrows=1)
    data = pd.read_fwf(filepath, skiprows=data_start_row) if read_data else None

    return MESAProfile(attributes, data)

class MESAProfile(object):
    def __init__(self, attributes, data):
        self.attributes = attributes
        self.data = data

    def __str__(self):
        return str(self.attributes) + "\n" + str(self.data)

    def get_attribute(self, attr):
        if self.has_attribute(attr):
            return self.attributes[attr].iloc[0]
        else:
            raise KeyError("Attribute \"" + attr + "\" is not a valid attribute for this MESA profile.")

    def has_attribute(self, attr):
        return attr in list(self.attributes.columns.values)
