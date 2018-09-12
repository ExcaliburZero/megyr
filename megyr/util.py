import datetime
import importlib.util
import os
import os.path
import subprocess

import pystache

COMPLETED_FILENAME = "completed.txt"

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def run_in_dir(command, directory):
    subprocess.call(command, cwd=directory, shell=True)

def render_mustache_file(f, values):
    renderer = pystache.Renderer()
    return renderer.render_path(f, values)

def load_py_module_from_file(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    new_module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(new_module)

    return new_module

def has_completed_file(directory):
    filepath = os.path.join(directory, COMPLETED_FILENAME)

    print("Checking: " + filepath)

    return os.path.isfile(filepath)

def create_completed_file(directory):
    filepath = os.path.join(directory, COMPLETED_FILENAME)

    with open(filepath, "w") as f:
        f.write(str(datetime.datetime.now()))
