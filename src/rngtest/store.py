import pickle
from datetime import datetime
from os import scandir
from pathlib import Path
from time import sleep

import numpy as np
import pandas as pd
from appdirs import AppDirs
from click import echo

import rngtest.profiling as profiling
from rngtest.slugify import slugify

__all__ = [
    "TYPES_MAP",
    "data_dir",
    "parse_data",
    "load",
    "load_with_profiles",
    "get_single_profiled_data",
    "get_profiled_data",
    "drop",
    "ls_stores",
]

dirs = AppDirs(appname="rngtest", appauthor="MatthewBarber")
data_dir = Path(dirs.user_data_dir)

# Create local data directory if it does not already exist
try:
    Path.mkdir(data_dir, parents=True)
    echo(f"Created store folder at {data_dir}")
except FileExistsError:
    pass

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


class TypeNotRecognizedError(ValueError):
    """Error for when an inputted dtype is not recognised"""

    pass


def parse_data(datafile, dtypestr=None) -> pd.DataFrame:
    """Reads file containing data into a dataframe"""
    df = pd.read_csv(datafile, header=None)

    if dtypestr is not None:
        try:
            dtype = TYPES_MAP[dtypestr]
        except KeyError:
            raise TypeNotRecognizedError()

        df = df.astype(dtype)
    else:
        df = df.infer_objects()

    return df


class StoreExistsError(FileExistsError):
    """Exception for when a store is being assumed to not exist but does"""

    pass


class NameConflictError(FileExistsError):
    """Error for when a unique storename could not be made"""

    pass


UNIQUE_STORENAME_ATTEMPTS = 3


def init_store(name=None, overwrite=False):
    """Creates store in local data

    :returns: The store's name and path
    """
    if name is not None:
        store_name = slugify(name)
        if store_name != name:
            echo(f"Store name {name} encoded as {store_name}")
    else:
        for _ in range(UNIQUE_STORENAME_ATTEMPTS):
            timestamp = datetime.now()
            store_name = timestamp.strftime("%Y%m%dT%H%M%SZ")

            if store_name not in ls_stores():
                break
            else:
                sleep(1.5)
        else:
            raise NameConflictError()

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

    return store_name, store_path


class MultipleColumnsError(ValueError):
    """Error for when only one column of data was expected"""

    pass


def load(datafile, name=None, dtypestr=None, overwrite=False):
    """Load RNG outputs into a store"""
    df = parse_data(datafile, dtypestr)

    if len(df.columns) > 1:
        raise MultipleColumnsError()
    series = df.iloc[:, 0]

    store_name, store_path = init_store(name=name, overwrite=overwrite)

    series = series.rename(store_name)
    data_path = store_path / PROFILED_DATA_FNAME
    pickle.dump(series, open(data_path, "wb"))


def load_with_profiles(
    datafile, profilespath, name=None, dtypestr=None, overwrite=False
):
    """Load profiled RNG outputs into a store"""
    df = parse_data(datafile, dtypestr)

    store_path = init_store(name=name, overwrite=overwrite)

    profiles = profiling.profiled_data(df, profilespath)

    for name, series in profiles:
        profile_name = slugify(name)
        if profile_name != name:
            echo(f"Profile name {name} encoded as {profile_name}")

        profile_path = store_path / profile_name
        Path.mkdir(profile_path, exist_ok=True)

        data_path = profile_path / PROFILED_DATA_FNAME
        pickle.dump(series, open(data_path, "wb"))


class StoreNotFoundError(FileNotFoundError):
    """Error for when requested store does not exist"""

    pass


class NotSingleProfiledError(LookupError):
    """Error for when requested store is not single-profiled"""

    pass


class NotMultiProfiledError(LookupError):
    """Error for when requested store is not profiled"""

    pass


def get_single_profiled_data(store_name) -> pd.Series:
    """Access data of a single-profiled store"""
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


def get_profiled_data(store_name) -> pd.Series:
    """Access data of a profiled store"""
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
    """Recursively remove files and folders in a given directory"""
    for child in path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def drop(store_name):
    """Remove store from local data"""
    store_path = data_dir / store_name

    rm_tree(store_path)


def ls_stores():
    """List all stores in local data"""
    for f in scandir(data_dir):
        if f.is_dir():
            yield f.name
