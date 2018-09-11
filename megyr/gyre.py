import os.path

import util

def run_gyre(config, values, rows, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name):
    gyre_dir_name = create_gyre_dir(config, mesa_comb, gyre_comb, output_dir, mesa_dir_name)

    extract_additional_values(config, gyre_comb, values, rows, work_dir)

    gyre_config = create_gyre_config(config, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name, gyre_dir_name)

    exec_gyre(config["gyre_location"], output_dir, mesa_dir_name, gyre_dir_name, gyre_config)

    return gyre_dir_name

def create_gyre_dir(config, mesa_comb, gyre_comb, output_dir, mesa_dir_name):
    dir_name = "gyre_"
    for key in gyre_comb:
        dir_name += key + "_" + str(gyre_comb[key]) + "__"

    gyre_dir = os.path.join(output_dir, mesa_dir_name, dir_name)

    print(gyre_dir)
    util.create_dir(gyre_dir)

    return dir_name

def extract_additional_values(config, gyre_comb, values, rows, work_dir):
    row = rows[rows["profile"] == gyre_comb["profile"]]

    if "gyre_values_module" in config:
        module_location = os.path.join(work_dir, config["gyre_values_module"])

        calculations_module = util.load_py_module_from_file("calculations", module_location)

        calculation_functions = calculations_module.values

        for key in calculation_functions:
            fun = calculation_functions[key]

            gyre_comb[key] = fun(row)

def create_gyre_config(config, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name, gyre_dir_name):
    end = -1 * len(".mustache")

    config_file = config["gyre_config"]
    config_file_in = os.path.join(work_dir, config_file)
    config_file_out = os.path.join(output_dir, mesa_dir_name, gyre_dir_name, config_file[:end])

    data = mesa_comb.copy()
    data["logs_dir"] = logs_dir_name
    data.update(gyre_comb)

    applied_contents = util.render_mustache_file(config_file_in, data)

    with open(config_file_out, "w") as out:
        out.write(applied_contents)

    print(data)
    print(config_file_out)

    return config_file[:end]

def exec_gyre(gyre_location, output_dir, mesa_dir_name, gyre_dir_name, gyre_config):
    gyre_dir = os.path.join(output_dir, mesa_dir_name, gyre_dir_name)

    gyre_command = gyre_location + " " + gyre_config

    util.run_in_dir(gyre_command, gyre_dir)
