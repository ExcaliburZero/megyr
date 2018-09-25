import datetime
import importlib.util
import os
import os.path
import subprocess
import sys

import pandas as pd
import pystache

COMPLETED_FILENAME = "completed.txt"

MP_THREADS_ENV_VAR = "OMP_NUM_THREADS"

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def run_in_dir(command, directory):
    subprocess.check_call(command, cwd=directory, shell=True)

def render_mustache_file(f, values):
    renderer = pystache.Renderer()
    return renderer.render_path(f, values)

def load_py_module_from_file(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    new_module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(new_module)

    return new_module

def has_completed_file(directory, filename=COMPLETED_FILENAME):
    filepath = os.path.join(directory, filename)

    return os.path.isfile(filepath)

def create_completed_file(directory, filename=COMPLETED_FILENAME):
    filepath = os.path.join(directory, filename)

    with open(filepath, "w") as f:
        f.write(str(datetime.datetime.now()))

def set_num_mp_threads(num):
    assert(num > 0)

    os.environ[MP_THREADS_ENV_VAR] = str(num)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class DataFrameAggregator(object):
    def __init__(self, should_read):
        self.data = pd.DataFrame()
        self.should_read = should_read

    def append_from_file(self, filepath, read_function=pd.read_csv, transform_func=lambda r: r):
        if self.should_read:
            new_rows = read_function(filepath)

            transformed = transform_func(new_rows)

            self.data = pd.concat([self.data, new_rows])

    def write_to_file(self, filepath):
        if self.should_read:
            self.data.to_csv(filepath, index=False)
        else:
            raise Exception("Tried to write out DataFrameAggregator that has reading disabled.")
