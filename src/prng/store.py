import pickle
from datetime import datetime
from os import scandir
from pathlib import Path

import numpy as np
import pandas as pd
from appdirs import AppDirs
from click import echo
from slugify import slugify

import prng.profiling as profiling

__all__ = [
    "DATA_FNAME",
    "PROFILES_FNAME",
    "PROFILED_DATA_FNAME",
    "data_dir",
    "parse_data",
    "load",
    "get_single_profiled_data",
    "get_profiled_data",
    "drop",
    "ls_stores",
]

DATA_FNAME = "dataframe.pickle"
PROFILES_FNAME = "profiles.pickle"
PROFILED_DATA_FNAME = "series.pickle"

TYPES_MAP = {
    "bool": np.bool_,
    "byte": np.byte,
    "short": np.int16,
    "int": np.int32,
    "long": np.int64,
    "float": np.float32,
    "double": np.float64,
}

dirs = AppDirs("prng")
data_dir = Path(dirs.user_data_dir)

try:
    Path.mkdir(data_dir)
    echo(f"Created store folder at {data_dir}")
except FileExistsError:
    pass


class StoreExistsError(FileExistsError):
    pass


def parse_data(data_file, dtype_str=None):
    df = pd.read_csv(data_file, header=None)

    if dtype_str is not None:
        # TODO regex check if np.foo or numpy.foo is used to get types directly
        try:
            dtype = TYPES_MAP[dtype_str]
        except KeyError:
            raise TypeNotRecognizedError()

        df = df.astype(dtype)
    else:
        df = df.infer_objects()

    return df


class MultipleColumnsError(ValueError):
    pass


class TypeNotRecognizedError(ValueError):
    pass


def init_store(name=None, overwrite=False):
    if name is not None:
        store_name = slugify(name)
        if store_name != name:
            echo(f"Store name {name} encoded as {store_name}")

    else:
        timestamp = datetime.now()
        store_name = timestamp.strftime("%Y%m%dT%H%M%SZ")
    # TODO check storename is available
    echo(f"Store name to be encoded as {store_name}")

    store_path = data_dir / store_name
    try:
        Path.mkdir(store_path)
    except FileExistsError:
        if overwrite:
            rm_tree(store_path)
            Path.mkdir(store_path)
        else:
            raise StoreExistsError()

    return store_path


def load(data_file, name=None, dtype_str=None, overwrite=False):
    df = parse_data(data_file, dtype_str)

    if len(df.columns) > 1:
        raise MultipleColumnsError()
    series = df.iloc[0]

    store_path = init_store(name=name, overwrite=overwrite)

    data_path = store_path / PROFILED_DATA_FNAME
    pickle.dump(series, open(data_path, "wb"))


def load_with_profiles(data_file, profiles_path, name=None, dtype_str=None, overwrite=False):
    df = parse_data(data_file, dtype_str)

    store_path = init_store(name=name, overwrite=overwrite)

    profiles = profiling.profiled_data(df, profiles_path)

    for name, series in profiles:
        profile_name = slugify(name)
        if profile_name != name:
            echo(f"Profile name {name} encoded as {profile_name}")

        profile_path = store_path / profile_name
        Path.mkdir(profile_path, exist_ok=True)

        data_path = profile_path / PROFILED_DATA_FNAME
        pickle.dump(series, open(data_path, "wb"))


def get_profiles(store_name):
    path = data_dir / store_name

    with open(path / PROFILES_FNAME, "rb") as f:
        profiles = pickle.load(f)

    return profiles


class StoreNotFoundError(FileNotFoundError):
    pass


class NotSingleProfiledError(Exception):
    pass


class NotMultiProfiledError(Exception):
    pass


def get_single_profiled_data(store_name):
    store_path = data_dir / store_name
    if not store_path.exists():
        raise StoreNotFoundError()

    single_profile_path = store_path / PROFILED_DATA_FNAME

    try:
        with open(single_profile_path, "rb") as f:
            series = pickle.load(f)

            return series

    except FileNotFoundError:
        raise NotSingleProfiledError()


def get_profiled_data(store_name):
    store_path = data_dir / store_name

    yield_count = 0

    try:
        for obj in scandir(store_path):
            if obj.is_dir():
                profile_path = Path(obj.path)
                with open(profile_path / PROFILED_DATA_FNAME, "rb") as f:
                    series = pickle.load(f)

                yield series
                yield_count += 1

        if yield_count == 0:
            raise NotMultiProfiledError()

    except FileNotFoundError:
        raise StoreNotFoundError()


def rm_tree(path):
    """Credit to https://stackoverflow.com/a/58183834/5193926"""
    for child in path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def drop(store_name):
    store_path = data_dir / store_name

    rm_tree(store_path)


def ls_stores():
    for f in scandir(data_dir):
        if f.is_dir():
            yield f.name
