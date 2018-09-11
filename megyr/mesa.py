import os.path

import pandas as pd

import util

def run_mesa(config, comb, output_dir):
    mesa_dir_name = create_mesa_dir(config, comb, output_dir)

    logs_dir_name = setup_mesa_dir(output_dir, mesa_dir_name)

    create_mesa_configs(config, comb, mesa_dir_name, logs_dir_name)

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

def create_mesa_configs(config, comb, mesa_dir_name, logs_dir_name):
    end = -1 * len(".mustache")

    for config_file in config["mesa_configs"]:
        config_file_out = os.path.join(mesa_dir_name, config_file[:end])

        data = comb.copy()
        data["logs_dir"] = logs_dir_name

        print(data)
        print(config_file_out)

def get_mesa_data(config, comb, mesa_dir):
    return ({}, pd.DataFrame({
        "star_age": [0, 1, 1000000009, 2000000000],
        "pulse": [0, 1, 2, 3]
    }))
