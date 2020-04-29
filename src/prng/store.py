import pickle
from datetime import datetime
from os import scandir
from pathlib import Path

import numpy as np
import pandas as pd
import toml
from appdirs import AppDirs
from click import echo
from slugify import slugify

__all__ = [
    "DATA_FNAME",
    "PROFILES_FNAME",
    "PROFILED_DATA_FNAME",
    "data_dir",
    "parse",
    "spec2profiles",
    "load",
    "get_data",
    "get_profiled_data",
    "drop",
    "ls_stores",
]

DATA_FNAME = "dataframe.pickle"
PROFILES_FNAME = "profiles.pickle"
PROFILED_DATA_FNAME = "series.pickle"

TYPES_MAP = {"float": np.single, "int": np.intc}

dirs = AppDirs("prng")
data_dir = Path(dirs.user_data_dir)

try:
    Path.mkdir(data_dir)
    echo(f"Created store folder at {data_dir}")
except FileExistsError:
    pass


class DataStoreExistsError(FileExistsError):
    pass


def parse(datafile, specfile):
    spec = toml.load(specfile)

    df = pd.read_csv(datafile, header=None)

    dtype = TYPES_MAP[spec["dtype"]]
    df = df.astype(dtype)

    return df, spec


def spec2profiles(spec):
    defaults = {"name": "DEFAULTS"}
    profiles = []

    # TODO single col
    # TODO autogen single col profiles

    for key, value in spec.items():
        if type(value) is dict:
            if key == "DEFAULTS":
                defaults = value
            else:
                profile = value
                profile["name"] = key
                profiles.append(profile)
        else:
            defaults[key] = value

    if len(profiles) == 0:
        profiles.append(defaults)
    else:
        for profile in profiles:
            for key, value in defaults.items():
                if key not in profile:
                    profile[key] = value

    return profiles


def cols(df):
    for col in df:
        yield df[col]


def profile_df(profile, df):
    if len(df.columns) == 1:
        s = df.iloc[:, 0]
    elif profile["concat"] == "columns":
        s = pd.concat(cols(df))
    elif profile["concat"] == "rows":
        s = pd.concat(cols(df.transpose()))
    else:
        raise NotImplementedError()

    return s


def load(datafile, specfile, overwrite=False):
    df, spec = parse(datafile, specfile)

    try:
        store_name = slugify(spec["name"])
    except KeyError:
        timestamp = datetime.now()
        store_name = timestamp.strftime("%Y%m%dT%H%M%SZ")
        # TODO check storename is valid
    echo(f"Store name encoded as {store_name}")

    store_path = data_dir / store_name
    try:
        Path.mkdir(store_path, exist_ok=overwrite)
    except FileExistsError:
        raise DataStoreExistsError()

    data_path = store_path / DATA_FNAME
    pickle.dump(df, open(data_path, "wb"))

    profiles = spec2profiles(spec)
    profiles_path = store_path / PROFILES_FNAME
    pickle.dump(profiles, open(profiles_path, "wb"))

    for profile in profiles:
        profile_name = slugify(profile["name"])
        if profile_name != profile["name"]:
            echo(f"Profile name {profile['name']} encoded as {profile_name}")

        profile_path = store_path / profile_name
        Path.mkdir(profile_path)

        series = profile_df(profile, df)

        series_path = profile_path / PROFILED_DATA_FNAME
        pickle.dump(series, open(series_path, "wb"))


def get_data(store_name):
    path = data_dir / store_name

    with open(path / DATA_FNAME, "rb") as f:
        data = pickle.load(f)

    return data


def get_profiles(store_name):
    path = data_dir / store_name

    with open(path / PROFILES_FNAME, "rb") as f:
        profiles = pickle.load(f)

    return profiles


def get_profiled_data(store_name):
    for obj in scandir(data_dir / store_name):
        if obj.is_dir():
            profile_path = Path(obj.path)
            with open(profile_path / PROFILED_DATA_FNAME, "rb") as f:
                series = pickle.load(f)

                yield series


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
