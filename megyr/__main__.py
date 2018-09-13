import argparse
import json
import os.path
import sys

import pandas as pd

import gyre
import mesa
import parameters
import util

def main():
    args = process_args(sys.argv)

    validate_args(args)

    with open(args.config_file, "r") as config_f:
        with open(args.params_file, "r") as params_f:
            config = json.load(config_f)
            validate_config(config)

            params = json.load(params_f)
            validate_params(params)

            megyr(config, params, args.work_dir)

def create_arg_parser():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("config_file", type=str, help="")
    parser.add_argument("params_file", type=str, help="")
    parser.add_argument("work_dir", type=str, help="")

    return parser

def process_args(argv):
    parser = create_arg_parser()

    return parser.parse_args(argv[1:])

def validate_args(args):
    assert(os.path.isfile(args.config_file))
    assert(os.path.isfile(args.params_file))
    assert(os.path.isdir(args.work_dir))

def validate_config(config):
    assert("output_dir" in config)
    assert("mesa_configs" in config)
    assert("gyre_config" in config)
    assert("mesa_profiles_summary_filename" in config)
    assert("star_exec_location" in config)
    assert("gyre_location" in config)
    assert("mesa_MP_threads" in config)
    assert("gyre_MP_threads" in config)

def validate_params(params):
    assert("mesa" in params)
    assert("gyre" in params)

def megyr(config, params, work_dir):
    output_dir = os.path.join(work_dir, config["output_dir"])

    util.create_dir(output_dir)

    mesa_grid = parameters.create_grid({}, [], params["mesa"])

    for comb in mesa_grid:
        print("MESA: " + str(comb))

        util.set_num_mp_threads(config["mesa_MP_threads"])

        mesa_dir_name, logs_dir_name = mesa.run_mesa(config, comb, work_dir, output_dir)

        values, rows = load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        gyre_grid = parameters.create_grid(values, rows, params["gyre"])

        util.set_num_mp_threads(config["gyre_MP_threads"])

        for gyre_comb in gyre_grid:
            print("GYRE: " + str(gyre_comb))
            gyre.run_gyre(config, values, rows, comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name)

def load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name):
    profiles_summary_file = os.path.join(output_dir, mesa_dir_name, config["mesa_profiles_summary_filename"])
    if os.path.isfile(profiles_summary_file):
        values = {}
        rows = pd.read_csv(profiles_summary_file)
    else:
        values, rows = mesa.get_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        rows.to_csv(profiles_summary_file, index=False)

    return values, rows

if __name__ == "__main__":
    main()
