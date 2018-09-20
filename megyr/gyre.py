import os.path

from . import util

def run_gyre(config, mesa_comb, mesa_data, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name):
    mesa_dir = os.path.join(output_dir, mesa_dir_name)
    gyre_dir_name = create_gyre_dir(mesa_dir)

    gyre_prefix = create_gyre_prefix(gyre_comb)

    gyre_completed = os.path.join(gyre_dir_name, "completed_" + gyre_prefix + ".txt")

    gyre_ad_output_summary = "summary_" + gyre_prefix + ".txt"
    gyre_comb["ad_output_summary_file"] = gyre_ad_output_summary

    if not util.has_completed_file(mesa_dir, filename=gyre_completed):
        derived = config["stages"]["gyre_derived"](mesa_comb, mesa_data, gyre_comb)

        gyre_config = create_gyre_config(config, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name, gyre_prefix, gyre_dir_name)

        exec_gyre(config["settings"]["gyre_location"], output_dir, mesa_dir_name, gyre_dir_name, gyre_config)
        util.create_completed_file(mesa_dir, filename=gyre_completed)
    else:
        print("Already completed GYRE")

    return os.path.join(output_dir, mesa_dir_name, gyre_dir_name, gyre_ad_output_summary)

def create_gyre_prefix(gyre_comb):
    name = "gyre_"
    for key in sorted(gyre_comb.keys()):
        name += key + "_" + str(gyre_comb[key]) + "__"

    return name

def create_gyre_dir(mesa_dir):
    gyre_dir_name = "gyre"

    gyre_dir = os.path.join(mesa_dir, gyre_dir_name)

    util.create_dir(gyre_dir)

    return gyre_dir_name

def create_gyre_config(config, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name, gyre_prefix, gyre_dir_name):
    end = -1 * len(".mustache")

    config_file = config["input"]["gyre_config"]
    config_file_in = os.path.join(work_dir, config_file)

    config_file_out_name = config_file[:end] + "_" + gyre_prefix
    config_file_out = os.path.join(output_dir, mesa_dir_name, gyre_dir_name, config_file_out_name)

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
