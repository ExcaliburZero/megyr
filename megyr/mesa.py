import os.path

import pandas as pd

import util

def run_mesa(config, comb, work_dir, output_dir):
    mesa_dir_name = create_mesa_dir(config, comb, output_dir)

    logs_dir_name = setup_mesa_dir(output_dir, mesa_dir_name)

    create_mesa_configs(config, comb, work_dir, output_dir, mesa_dir_name, logs_dir_name)

    exec_mesa(config, work_dir, output_dir, mesa_dir_name)

    return mesa_dir_name, logs_dir_name

def create_mesa_dir(config, comb, output_dir):
    dir_name = "mesa_"
    for key in comb:
        dir_name += key + "_" + str(comb[key]) + "__"

    mesa_dir = os.path.join(output_dir, dir_name)

    print(mesa_dir)
    util.create_dir(mesa_dir)

    return dir_name

def setup_mesa_dir(output_dir, mesa_dir_name):
    logs_dir_name = "LOGS"
    logs_dir = os.path.join(output_dir, mesa_dir_name, logs_dir_name)

    print(logs_dir)
    util.create_dir(logs_dir)

    return logs_dir_name

def create_mesa_configs(config, comb, work_dir, output_dir, mesa_dir_name, logs_dir_name):
    end = -1 * len(".mustache")

    for config_file in config["mesa_configs"]:
        config_file_in = os.path.join(work_dir, config_file)
        config_file_out = os.path.join(output_dir, mesa_dir_name, config_file[:end])

        data = comb.copy()
        data["logs_dir"] = logs_dir_name

        applied_contents = util.render_mustache_file(config_file_in, data)

        with open(config_file_out, "w") as out:
            out.write(applied_contents)

        print(data)
        print(config_file_out)

def exec_mesa(config, work_dir, output_dir, mesa_dir_name):
    mesa_dir = os.path.join(output_dir, mesa_dir_name)

    mesa_command = os.path.abspath(
	os.path.join(work_dir, config["star_exec_location"])
    )

    util.run_in_dir(mesa_command, mesa_dir)

def get_mesa_data(config, comb, mesa_dir):
    return ({}, pd.DataFrame({
        "star_age": [0, 1, 1000000009, 2000000000],
        "pulse": [0, 1, 2, 3]
    }))
