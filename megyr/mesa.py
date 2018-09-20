import os.path

import pandas as pd

from . import profile
from . import util

def run_mesa(config, comb, work_dir, output_dir):
    mesa_dir_name = create_mesa_dir(config, comb, output_dir)

    logs_dir_name = setup_mesa_dir(output_dir, mesa_dir_name)

    mesa_dir = os.path.join(output_dir, mesa_dir_name)
    if not util.has_completed_file(mesa_dir):
        derived = extract_additional_values(config, comb)

        create_mesa_configs(config, derived, work_dir, output_dir, mesa_dir_name, logs_dir_name)

        exec_mesa(config, work_dir, output_dir, mesa_dir_name)

        util.create_completed_file(mesa_dir)
    else:
        print("Already completed MESA")

    return mesa_dir_name, logs_dir_name

def create_mesa_dir(config, comb, output_dir):
    dir_name = "mesa_"
    for key in sorted(comb.keys()):
        dir_name += key + "_" + str(comb[key]) + "__"

    mesa_dir = os.path.join(output_dir, dir_name)

    util.create_dir(mesa_dir)

    return dir_name

def extract_additional_values(config, mesa_comb):
    if "mesa_derived" in config["stages"]:
        return config["stages"]["mesa_derived"](mesa_comb)

    return dict(mesa_comb)

def setup_mesa_dir(output_dir, mesa_dir_name):
    logs_dir_name = "LOGS"
    logs_dir = os.path.join(output_dir, mesa_dir_name, logs_dir_name)

    util.create_dir(logs_dir)

    return logs_dir_name

def create_mesa_configs(config, comb, work_dir, output_dir, mesa_dir_name, logs_dir_name):
    end = -1 * len(".mustache")

    for config_file in config["input"]["mesa_configs"]:
        config_file_in = os.path.join(work_dir, config_file)
        config_file_out = os.path.join(output_dir, mesa_dir_name, config_file[:end])

        data = comb.copy()
        data["logs_dir"] = logs_dir_name

        applied_contents = util.render_mustache_file(config_file_in, data)

        with open(config_file_out, "w") as out:
            out.write(applied_contents)

def exec_mesa(config, work_dir, output_dir, mesa_dir_name):
    mesa_dir = os.path.join(output_dir, mesa_dir_name)

    mesa_command = os.path.abspath(
	os.path.join(work_dir, config["settings"]["mesa_star_location"])
    )

    util.run_in_dir(mesa_command, mesa_dir)

def get_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name):
    logs_dir = os.path.join(output_dir, mesa_dir_name, logs_dir_name)

    profile_index_name = "profiles.index"
    profile_index = os.path.join(logs_dir, profile_index_name)

    num_profiles = profile.read_num_profiles(profile_index)

    data = profile.read_all_profile_attributes(logs_dir, num_profiles)

    return {}, data
