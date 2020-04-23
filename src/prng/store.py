import pickle
import re
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import toml
from appdirs import AppDirs
from click import echo
from slugify import slugify

__all__ = ["store", "manifest_keys"]

r_newlines = re.compile("\r\n?|\n")

MANIFEST_FNAME = "manifest.pickle"
DATA_FNAME = "data.pickle"

TYPES_MAP = {"float": np.single}

dirs = AppDirs("prng")
data_dir = Path(dirs.user_data_dir)
manifest_path = data_dir / MANIFEST_FNAME

try:
    Path.mkdir(data_dir)
    echo(f"Created store folder at {data_dir}")
except FileExistsError:
    pass


class DataStoreExistsError(FileExistsError):
    pass


@contextmanager
def open_manifest():
    if not manifest_path.exists():
        manifest = {}
    else:
        with open(manifest_path, "rb") as f:
            try:
                manifest = pickle.load(f)
            except EOFError:
                manifest = {}

    with open(manifest_path, "wb") as f:
        yield manifest
        pickle.dump(manifest, f)


def escape_newlines(lines):
    for line in lines:
        yield re.sub(r_newlines, "", line)


def store(data, spec, overwrite=False):
    spec = toml.load(spec)

    store_name = slugify(spec["name"])
    echo(f"Store name encoded as {store_name}")

    store_path = data_dir / store_name
    try:
        Path.mkdir(store_path, exist_ok=overwrite)
    except FileExistsError:
        raise DataStoreExistsError()
    echo(f"Created store cache at {store_path}")

    dtype = TYPES_MAP[spec["type"]]
    array = escape_newlines(data.readlines())
    array = np.array(list(array), dtype=dtype)

    # TODO profile stuff i.e. for profile in spec.profiles

    data_path = store_path / DATA_FNAME
    pickle.dump(array, open(data_path, "wb"))

    with open_manifest() as manifest:
        manifest["store_name"] = data_path


def manifest_keys():
    with open_manifest() as manifest:
        return manifest.keys()