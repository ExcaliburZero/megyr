import os
import subprocess

import pystache

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def run_in_dir(command, directory):
    subprocess.call(command, cwd=directory, shell=True)

def render_mustache_file(f, values):
    renderer = pystache.Renderer()
    return renderer.render_path(f, values)
