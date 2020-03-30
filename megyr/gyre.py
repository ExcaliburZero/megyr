import os.path

from . import util


def run_gyre(
    config,
    mesa_comb,
    mesa_data,
    gyre_comb,
    work_dir,
    output_dir,
    mesa_dir_name,
    logs_dir_name,
    gyre_dir_name,
    gyre_prefix,
    gyre_ad_output_summary,
):
    mesa_dir = os.path.join(output_dir, mesa_dir_name)

    gyre_dir = os.path.join(mesa_dir, gyre_dir_name)
    util.create_dir(gyre_dir)

    derived = extract_additional_values(config, mesa_comb, mesa_data, gyre_comb)

    derived["ad_output_summary_file"] = gyre_ad_output_summary

    gyre_config = create_gyre_config(
        config,
        mesa_comb,
        derived,
        work_dir,
        output_dir,
        mesa_dir_name,
        logs_dir_name,
        gyre_prefix,
        gyre_dir_name,
    )

    exec_gyre(
        config["settings"]["gyre_location"],
        output_dir,
        mesa_dir_name,
        gyre_dir_name,
        gyre_config,
    )


def extract_additional_values(config, mesa_comb, mesa_data, gyre_comb):
    if "gyre_derived" in config["stages"]:
        return config["stages"]["gyre_derived"](mesa_comb, mesa_data, gyre_comb)

    return dict(gyre_comb)


def create_gyre_prefix(gyre_comb):
    """
    Creates a GYRE run prefix to use for the given combination of GYRE
    parameter values. These prefixes should be unique within one MESA run, but
    can be repeated across multiple, separate, MESA runs.

    This also needs to be deterministic, reguardless of the fact that the dict
    passed in is unordered.

    >>> create_gyre_prefix({"a": 2, "c": 3, "b": "hi"})
    'gyre_a_2__b_hi__c_3__'
    """
    name = "gyre_"
    for key in sorted(gyre_comb.keys()):
        name += key + "_" + str(gyre_comb[key]) + "__"

    return name


def create_gyre_config(
    config,
    mesa_comb,
    gyre_comb,
    work_dir,
    output_dir,
    mesa_dir_name,
    logs_dir_name,
    gyre_prefix,
    gyre_dir_name,
):
    end = -1 * len(".mustache")

    config_file = config["input"]["gyre_config"]
    config_file_in = os.path.join(work_dir, config_file)

    config_file_out_name = config_file[:end] + "_" + gyre_prefix
    config_file_out = os.path.join(
        output_dir, mesa_dir_name, gyre_dir_name, config_file_out_name
    )

    data = mesa_comb.copy()
    data["logs_dir"] = logs_dir_name

    data.update(gyre_comb)
    data["gyre_dir"] = gyre_dir_name

    applied_contents = util.render_mustache_file(config_file_in, data)

    with open(config_file_out, "w") as out:
        out.write(applied_contents)

    return config_file_out_name


def exec_gyre(gyre_location, output_dir, mesa_dir_name, gyre_dir_name, gyre_config):
    gyre_dir = os.path.join(output_dir, mesa_dir_name, gyre_dir_name)

    gyre_command = gyre_location + " " + gyre_config

    util.run_in_dir(gyre_command, gyre_dir)
