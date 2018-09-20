import argparse
import json
import os.path
import sys

import pandas as pd

from . import gyre
from . import mesa
from . import oscillations_summary
from . import parameters
from . import util

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

def run(config):
    validate_config(config)

    work_dir = "."
    output_dir = os.path.join(work_dir, config["output"]["output_dir"])

    util.create_dir(output_dir)

    mesa_params = config["stages"]["mesa_params"]
    mesa_grid = parameters.create_grid({}, [], mesa_params)

    for comb in mesa_grid:
        print("MESA: " + str(comb))

        util.set_num_mp_threads(config["settings"]["mesa_mp_threads"])

        mesa_dir_name, logs_dir_name = mesa.run_mesa(config, comb, work_dir, output_dir)

        values, rows = load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        # TODO: Add preivously calculated mesa values to "values"

        if "gyre" in params:
            gyre_grid = parameters.create_grid(values, rows, params["gyre"])

            util.set_num_mp_threads(config["gyre_MP_threads"])

            gyre_grid = parameters.create_grid(values, rows, params["gyre"])

            util.set_num_mp_threads(config["gyre_MP_threads"])

            oscillations = pd.DataFrame()
            for gyre_comb in gyre_grid:
                print("GYRE: " + str(gyre_comb))
                ad_output_summary_file = gyre.run_gyre(config, values, rows, comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name)

                summary = oscillations_summary.read_oscillations_summary_file(ad_output_summary_file).data

                for key in gyre_comb:
                    v = gyre_comb[key]

                    summary[key] = v

                oscillations = pd.concat([oscillations, summary])

            oscillations_file = os.path.join(output_dir, mesa_dir_name, config["gyre_oscillations_summary_filename"])
            oscillations.to_csv(oscillations_file, index=False)

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
    pass

def validate_params(params):
    assert("mesa" in params)

def megyr(config, params, work_dir):
    output_dir = os.path.join(work_dir, config["output_dir"])

    util.create_dir(output_dir)

    mesa_grid = parameters.create_grid({}, [], params["mesa"])

    for comb in mesa_grid:
        print("MESA: " + str(comb))

        util.set_num_mp_threads(config["mesa_MP_threads"])

        mesa_dir_name, logs_dir_name = mesa.run_mesa(config, comb, work_dir, output_dir)

        values, rows = load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        # TODO: Add preivously calculated mesa values to "values"

        if "gyre" in params:
            gyre_grid = parameters.create_grid(values, rows, params["gyre"])

            util.set_num_mp_threads(config["gyre_MP_threads"])

            gyre_grid = parameters.create_grid(values, rows, params["gyre"])

            util.set_num_mp_threads(config["gyre_MP_threads"])

            oscillations = pd.DataFrame()
            for gyre_comb in gyre_grid:
                print("GYRE: " + str(gyre_comb))
                ad_output_summary_file = gyre.run_gyre(config, values, rows, comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name)

                summary = oscillations_summary.read_oscillations_summary_file(ad_output_summary_file).data

                for key in gyre_comb:
                    v = gyre_comb[key]

                    summary[key] = v

                oscillations = pd.concat([oscillations, summary])

            oscillations_file = os.path.join(output_dir, mesa_dir_name, config["gyre_oscillations_summary_filename"])
            oscillations.to_csv(oscillations_file, index=False)

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
