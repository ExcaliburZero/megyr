from typing import Any, Callable, cast, Dict, List, Optional, Tuple

import argparse
import datetime
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


def run(config: Dict[str, Any]) -> None:
    config_errors = config_validation.validate_config(config)

    config_validation.set_defaults(config)

    if len(config_errors) > 0:
        handle_config_errors(config_errors)

    work_dir = "."
    output_dir = os.path.join(work_dir, config["output"]["output_dir"])

    util.create_dir(output_dir)

    completed_tasks, completed_filepath = get_completed_tasks(config)

    mesa_params = config["stages"]["mesa_params"]

    # Get or calculate the mesa param grid
    if isinstance(mesa_params, dict):
        mesa_grid = parameters.create_grid([], mesa_params)
    else:
        mesa_grid = mesa_params

    for mesa_comb in mesa_grid:
        print("MESA: " + str(mesa_comb))

        if config_validation.nested_in(config, ["settings", "mesa_mp_threads"]):
            util.set_num_mp_threads(config["settings"]["mesa_mp_threads"])

        mesa_dir_name = mesa.create_mesa_dir_name(mesa_comb)
        logs_dir_name = "LOGS"

        if task_not_completed(completed_tasks, mesa_dir_name):
            mesa_task = lambda: mesa.run_mesa(
                config, mesa_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name
            )
            run_task(completed_filepath, completed_tasks, mesa_dir_name, mesa_task)
        else:
            print("Already completed MESA")

        mesa_data = load_or_collect_mesa_data(
            config, output_dir, mesa_dir_name, logs_dir_name
        )

        # TODO: Add preivously calculated mesa values to "values"

        if config_validation.should_run_gyre(config):
            gyre_params = config["stages"]["gyre_params"](mesa_params, mesa_data)

            gyre_grid = parameters.create_grid(mesa_data, gyre_params)

            if config_validation.nested_in(config, ["settings", "gyre_mp_threads"]):
                util.set_num_mp_threads(config["settings"]["gyre_mp_threads"])

            record_oscill_ad = config_validation.nested_in(
                config, ["output", "gyre_oscillations_ad_summary_file"]
            )

            oscillations_ad = util.DataFrameAggregator(should_read=record_oscill_ad)
            for gyre_comb in gyre_grid:
                print("GYRE: " + str(gyre_comb))
                gyre_dir_name = "gyre"
                gyre_prefix = gyre.create_gyre_prefix(gyre_comb)

                gyre_task_name = mesa_dir_name + "-" + gyre_prefix

                ad_output_summary = "summary_" + gyre_prefix + ".txt"
                ad_output_summary_file = os.path.join(
                    output_dir, mesa_dir_name, gyre_dir_name, ad_output_summary
                )

                def transform_oscillations(rows: pd.DataFrame) -> pd.DataFrame:
                    for key in gyre_comb:
                        v = gyre_comb[key]

                        rows[key] = v

                    return rows

                read_ad: Callable[[], None] = lambda: oscillations_ad.append_from_file(
                    filepath=ad_output_summary_file,
                    read_function=load_ad_summary_file,
                    transform_func=transform_oscillations,
                )

                if task_not_completed(completed_tasks, gyre_task_name):

                    def gyre_task() -> None:
                        gyre.run_gyre(
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
                            ad_output_summary,
                        )
                        read_ad()

                    run_task(
                        completed_filepath, completed_tasks, gyre_task_name, gyre_task
                    )
                else:
                    print("Already completed GYRE")

                    read_ad()

            if config_validation.nested_in(
                config, ["output", "gyre_oscillations_ad_summary_file"]
            ):
                oscillations_ad_file = os.path.join(
                    output_dir,
                    mesa_dir_name,
                    config["output"]["gyre_oscillations_ad_summary_file"],
                )

                oscillations_ad.write_to_file(oscillations_ad_file)


def handle_config_errors(config_errors: List[str]) -> None:
    util.eprint("Found {} config errors.\n".format(len(config_errors)))

    for i in range(1, len(config_errors) + 1):
        util.eprint("{}) {}\n".format(i, config_errors[i - 1]))

    sys.exit(1)


def load_or_collect_mesa_data(
    config: Dict[str, Any], output_dir: str, mesa_dir_name: str, logs_dir_name: str
) -> pd.DataFrame:
    filename = cast(str, config["output"]["mesa_profile_summary_file"])

    get_summary_file_name: Callable[[], str] = lambda: os.path.join(
        output_dir, mesa_dir_name, filename
    )

    if filename is not None and os.path.isfile(get_summary_file_name()):
        rows = pd.read_csv(get_summary_file_name())
    else:
        rows = mesa.get_mesa_data(config, output_dir, mesa_dir_name, logs_dir_name)

        if filename is not None:
            rows.to_csv(get_summary_file_name(), index=False)

    return rows


def load_oscillations_file(
    filepath: str, file_not_found_handler: Optional[Callable[[str], None]] = None
) -> pd.DataFrame:
    try:
        return oscillations_summary.read_oscillations_summary_file(filepath).data
    except FileNotFoundError as e:
        if file_not_found_handler is not None:
            file_not_found_handler(filepath)
        else:
            raise e


def load_ad_summary_file(filepath: str) -> pd.DataFrame:
    return load_oscillations_file(
        filepath, file_not_found_handler=handle_missing_ad_summary
    )


def handle_missing_ad_summary(filepath: str) -> None:
    util.print_runtime_error_divider()

    util.eprint(
        "[missing_ad_summary_file] Failed to load adiabatic oscillation summary file: {}\n".format(
            filepath
        )
    )
    util.eprint(
        "Make sure that you are using the correct filepath for 'summary_file' in your GYRE config file.\n"
    )
    util.eprint(
        "See the configuration documentation for the 'gyre_oscillations_ad_summary_file' config value for more info."
    )

    sys.exit(1)


def get_completed_tasks(config: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    completed_filepath = "completed_tasks.csv"

    try:
        return pd.read_csv(completed_filepath), completed_filepath
    except FileNotFoundError:
        completed = pd.DataFrame(
            {"task_name": [], "start": [], "end": [], "duration": []}
        )

        completed.to_csv(completed_filepath, index=False)

        return completed, completed_filepath


def task_not_completed(completed: pd.DataFrame, task_name: str) -> bool:
    return task_name not in list(completed["task_name"])


def run_task(
    filepath: str,
    completed: List[pd.DataFrame],
    task_name: str,
    task_function: Callable[[], None],
) -> None:
    start = datetime.datetime.now()
    task_function()
    end = datetime.datetime.now()

    duration = (end - start).seconds

    completed.append(
        pd.DataFrame(
            {
                "task_name": [task_name],
                "start": [start],
                "end": [end],
                "duration": [duration],
            }
        )
    )

    with open(filepath, "a") as f:
        new_row = ",".join([task_name, str(start), str(end), str(duration)])

        f.write(new_row + "\n")
