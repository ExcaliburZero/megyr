import argparse
import json
import os.path
import sys

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
    assert("gyre_configs" in config)
    assert("star_exec_location" in config)

def validate_params(params):
    assert("mesa" in params)
    assert("gyre" in params)

def megyr(config, params, work_dir):
    output_dir = os.path.join(work_dir, config["output_dir"])

    print(output_dir)
    util.create_dir(output_dir)

    mesa_grid = parameters.create_grid({}, [], params["mesa"])

    for comb in mesa_grid:
        print(comb)

        # TODO: Fix mesa_dir to mesa_dir_name
        mesa_dir, logs_dir = mesa.run_mesa(config, comb, output_dir)

        values, rows = mesa.get_mesa_data(config, comb, mesa_dir)

        gyre_grid = parameters.create_grid(values, rows, params["gyre"])

        for gyre_comb in gyre_grid:
            print("\t" + str(gyre_comb))
            run_gyre(config, gyre_comb)

def run_gyre(config, comb):
    pass

if __name__ == "__main__":
    main()
