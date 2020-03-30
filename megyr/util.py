from typing import Any, Callable, cast, Dict, List

import datetime
import importlib.util
import os
import os.path
import subprocess
import sys

import pandas as pd
import pystache

MP_THREADS_ENV_VAR = "OMP_NUM_THREADS"


def create_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run_in_dir(command: List[str], directory: str) -> None:
    subprocess.check_call(command, cwd=directory, shell=True)


def render_mustache_file(f: str, values: Dict[str, str]) -> str:
    renderer = pystache.Renderer()
    return cast(str, renderer.render_path(f, values))


def set_num_mp_threads(num: int) -> None:
    assert num > 0

    os.environ[MP_THREADS_ENV_VAR] = str(num)


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def print_runtime_error_divider() -> None:
    eprint("------------------------")


class DataFrameAggregator:
    def __init__(self, should_read: bool) -> None:
        self.data = pd.DataFrame()
        self.should_read = should_read

    def append_from_file(
        self,
        filepath: str,
        read_function: Callable[[str], pd.DataFrame] = pd.read_csv,
        transform_func: Callable[[pd.DataFrame], pd.DataFrame] = lambda r: r,
    ) -> None:
        if self.should_read:
            new_rows = read_function(filepath)

            transformed = transform_func(new_rows)

            self.data = pd.concat([self.data, new_rows])

    def write_to_file(self, filepath: str) -> None:
        if self.should_read:
            self.data.to_csv(filepath, index=False)
        else:
            raise Exception(
                "Tried to write out DataFrameAggregator that has reading disabled."
            )
