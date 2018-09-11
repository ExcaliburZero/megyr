import os

def create_dir(path):
    os.makedirs(path, exist_ok=True)
