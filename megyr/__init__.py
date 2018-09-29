import argparse
import json
import os.path
import sys

import pandas as pd

from . import config_validation
from . import gyre
from . import mesa
from . import oscillations_summary
from . import parameters
from . import util

def run(config):
    config_errors = config_validation.validate_config(config)

    config_validation.set_defaults(config)

    if len(config_errors) > 0:
        util.eprint("Found {} config errors.\n".format(len(config_errors)))

        for i in range(1, len(config_errors) + 1):
            util.eprint("{}) {}\n".format(i, config_errors[i - 1]))

        sys.exit(1)

    work_dir = "."
    output_dir = os.path.join(work_dir, config["output"]["output_dir"])

    util.create_dir(output_dir)

    mesa_params = config["stages"]["mesa_params"]
    mesa_grid = parameters.create_grid({}, [], mesa_params)

    for mesa_comb in mesa_grid:
        print("MESA: " + str(mesa_comb))

        if config_validation.nested_in(config, ["settings", "mesa_mp_threads"]):
            util.set_num_mp_threads(config["settings"]["mesa_mp_threads"])

        mesa_dir_name, logs_dir_name = mesa.run_mesa(config, mesa_comb, work_dir, output_dir)

        mesa_data = load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        # TODO: Add preivously calculated mesa values to "values"

        if config_validation.should_run_gyre(config):
            gyre_params = config["stages"]["gyre_params"](mesa_params, mesa_data)

            gyre_grid = parameters.create_grid({}, mesa_data, gyre_params)

            if config_validation.nested_in(config, ["settings", "gyre_mp_threads"]):
                util.set_num_mp_threads(config["settings"]["gyre_mp_threads"])

            record_oscill_ad = config_validation.nested_in(config, ["output", "gyre_oscillations_ad_summary_file"])

            oscillations_ad = util.DataFrameAggregator(
                should_read=record_oscill_ad
            )
            for gyre_comb in gyre_grid:
                print("GYRE: " + str(gyre_comb))
                ad_output_summary_file = gyre.run_gyre(config, mesa_comb, mesa_data, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name)

                def transform_oscillations(rows):
                    for key in gyre_comb:
                        v = gyre_comb[key]

                        rows[key] = v

                    return rows

                oscillations_ad.append_from_file(
                    filepath=ad_output_summary_file,
                    read_function=load_ad_summary_file,
                    transform_func=transform_oscillations
                )

            if config_validation.nested_in(config, ["output", "gyre_oscillations_ad_summary_file"]):
                oscillations_ad_file = os.path.join(output_dir, mesa_dir_name, config["output"]["gyre_oscillations_ad_summary_file"])

                oscillations_ad.write_to_file(oscillations_ad_file)

def load_or_collect_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name):
    filename = config["output"]["mesa_profile_summary_file"]
    profiles_summary_file = os.path.join(output_dir, mesa_dir_name, filename)
    if os.path.isfile(profiles_summary_file):
        rows = pd.read_csv(profiles_summary_file)
    else:
        rows = mesa.get_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        rows.to_csv(profiles_summary_file, index=False)

    return rows

def load_oscillations_file(filepath, file_not_found_handler=None):
    try:
        return oscillations_summary.read_oscillations_summary_file(filepath).data
    except FileNotFoundError as e:
        if file_not_found_handler is not None:
            file_not_found_handler(filepath)
        else:
            raise e

def load_ad_summary_file(filepath):
    return load_oscillations_file(
        filepath,
        file_not_found_handler=handle_missing_ad_summary
    )

def handle_missing_ad_summary(filepath):
    util.print_runtime_error_divider()

    util.eprint("[missing_ad_summary_file] Failed to load adiabatic oscillation summary file: {}\n".format(filepath))
    util.eprint("Make sure that you are using the correct filepath for 'summary_file' in your GYRE config file.\n")
    util.eprint("See the configuration documentation for the 'gyre_oscillations_ad_summary_file' config value for more info.")

    sys.exit(1)
