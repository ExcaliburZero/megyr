import pandas as pd


def read_oscillations_summary_file(
    filepath, attributes_start_row=2, data_start_row=5, column_width=25
):
    num_attributes = get_num_attributes(filepath, attributes_start_row)

    attr_widths = [column_width for _ in range(0, num_attributes)]

    attributes = pd.read_fwf(
        filepath, skiprows=attributes_start_row, nrows=1, widths=attr_widths
    )
    data = pd.read_fwf(filepath, skiprows=data_start_row)

    return OscillationsSummary(attributes, data)


def get_num_attributes(filepath, attributes_start_row):
    with open(filepath) as f:
        for i, line in enumerate(f):
            if i == attributes_start_row - 1:
                return len(line.split())

    raise Exception(
        "Unable to find attributes column number line in oscillations summary file."
    )


class OscillationsSummary(object):
    def __init__(self, attributes, data):
        self.attributes = attributes
        self.data = data

    def __str__(self):
        return str(self.attributes) + "\n" + str(self.data)

    def get_attribute(self, attr):
        if self.has_attribute(attr):
            return self.attributes[attr].iloc[0]
        else:
            raise KeyError(
                'Attribute "'
                + attr
                + '" is not a valid attribute for this oscillations summary.'
            )

    def has_attribute(self, attr):
        return attr in list(self.attributes.columns.values)
