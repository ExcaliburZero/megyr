import os.path

import util

def run_gyre(config, mesa_comb, gyre_comb, work_dir, output_dir, mesa_dir_name, logs_dir_name):
    gyre_dir_name = create_gyre_dir(config, mesa_comb, gyre_comb, output_dir, mesa_dir_name)

    gyre_comb["freq_min"] = 1
    gyre_comb["freq_max"] = 100

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
