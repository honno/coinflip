"""Store functionality for the CLI

Notes
-----
A store is an abstraction for a folder in the user's local data directory
which pertains to a specific dataset that comprises of RNG output. The store can
subsequently store test results and report markup for said results.
"""
import pickle
import shelve
from contextlib import contextmanager
from datetime import datetime
from os import scandir
from pathlib import Path
from time import sleep
from typing import Dict
from warnings import warn

import numpy as np
import pandas as pd
from appdirs import AppDirs
from slugify import slugify

from rngtest.randtests._exceptions import NonBinarySequenceError
from rngtest.randtests._result import TestResult

__all__ = [
    "TYPES",
    "data_dir",
    "DataParsingError",
    "parse_data",
    "StoreError",
    "init_store",
    "store_data",
    "NoLatestStoreRecordedError",
    "find_latest_store",
    "get_data",
    "drop",
    "list_stores",
    "store_result",
    "store_results",
    "open_results",
]

dirs = AppDirs(appname="rngtest", appauthor="MatthewBarber")
data_dir = Path(dirs.user_data_dir)

# Create local data directory if it does not already exist
try:
    Path.mkdir(data_dir, parents=True)
except FileExistsError:
    pass

LATEST_STORE_FNAME = "latest_store.txt"
DATA_FNAME = "series.pickle"
RESULTS_FNAME = "results"  # shelve appends .db to filepaths

# ------------------------------------------------------------------------------
# Store initialisation

TYPES = {
    "bool": np.bool_,
    "byte": np.byte,
    "short": np.int16,
    "int": np.int32,
    "long": np.int64,
    "float": np.float32,
    "double": np.float64,
}


class DataParsingError(ValueError):
    """Base class for parsing-related errors"""


class TypeNotRecognizedError(DataParsingError):
    """Error for when a given dtype string representation is not recognised"""

    def __init__(self, dtype: str):
        self.dtype = dtype

    def __str__(self):
        f_types = ", ".join(TYPES.keys())
        return f"{self.dtype} is not a recognised data type\n" f"Valid types: {f_types}"


class MultipleColumnsError(DataParsingError):
    """Error for when only one column of data was expected"""

    def __init__(self, ncols):
        self.ncols = ncols

    def __str__(self):
        return (
            f"Parsed data contains {self.ncols} columns, but only 1 column was expected"
        )


def parse_data(data_file, dtype_str=None) -> pd.Series:
    """Reads file containing data into a pandas Series

    Reads from file containing RNG output and produces a representitive pandas
    Series. The appropiate dtype is inferred from the data itself, or optionally
    from the supplied `dtype_str`.

    Parameters
    ----------
    data_file : file-like object
        File containing RNG output
    dtype_str : `str`, optional
        String representation of desired dtype. If not supplied, it is inferred
        from the data.

    Returns
    -------
    `Series`
        A pandas `Series` which represents the data

    Raises
    ------
    TypeNotRecognizedError
        If supplied dtype_str does not recognise a dtype
    MultipleColumnsError
        If inputted data contains multiple values per line
    NonBinarySequenceError
        If sequence does not contain only 2 values

    See Also
    --------
    pandas.read_csv : The pandas method for reading `data_file`
    store_data : Calls this method, and handles subsequent storage of data
    """
    df = pd.read_csv(data_file, header=None)

    ncols = len(df.columns)
    if ncols > 1:
        raise MultipleColumnsError(ncols)
    series = df.iloc[:, 0]

    if series.nunique() != 2:
        raise NonBinarySequenceError()

    if dtype_str is not None:
        try:
            dtype = TYPES[dtype_str]
        except KeyError:
            raise TypeNotRecognizedError(dtype_str)

        series = series.astype(dtype)
    else:
        series = series.infer_objects()

    return series


class StoreError(Exception):
    """Base class for store-related errors"""

    def __init__(self, store_name):
        self.store_name = store_name


class StoreExistsError(StoreError, FileExistsError):
    """Error for when a store is being assumed to not exist but does"""

    def __str__(self):
        return (
            f"'{self.store_name}' already exists\n"
            "Use the --overwrite flag to write over this store"
        )


class NameConflictError(StoreError, FileExistsError):
    """Error for when a unique storename could not be made"""

    def __str__(self):
        return f"Generated name '{self.store_name}' conflicted with existing store"


def init_store(name=None, overwrite=False):
    """Creates store in local data

    A name supplied or generated is used to initialise a store. If supplied,
    the name is sanitised to remove invalid characters for filepaths. If
    generated, the name will be a timestamp of initialisation.

    Parameters
    ----------
    name : `str`, optional
        Desired name of the store, which will be sanitised. If not supplied, a
        name is generated automatically.
    overwrite : `boolean`, default `False`
        If a name conflicts with an existing store, this decides whether to
        overwrite it.

    Returns
    -------
    store_name : `str`
        Internal name of the initialised store
    store_path : `Path`
        Path of the initialised store

    Raises
    ------
    NameConflictError
        If attempts at generating a unique name fails
    StoreExistsError
        If a store of the same name exists already (and overwrite is set to
        `False`)
    NonBinarySequenceError
        If sequence does not contain only 2 values

    See Also
    --------
    store_data : Parses data and calls this method, to then save data in store
    """
    if name is not None:
        store_name = slugify(name, separator="_")

        if store_name != name:
            warn(f"Name encoded as {store_name}", UserWarning)

    else:
        for _ in range(3):
            timestamp = datetime.now()
            iso8601 = timestamp.strftime("%Y%m%dT%H%M%SZ")
            store_name = f"store_{iso8601}"

            if store_name not in list_stores():
                break
            else:
                sleep(1.5)
        else:
            raise NameConflictError(store_name)

        print(f"Store name to be encoded as {store_name}")

    store_path = data_dir / store_name
    try:
        Path.mkdir(store_path, parents=True)
    except FileExistsError:
        if overwrite:
            rm_tree(store_path)
            Path.mkdir(store_path)
        else:
            raise StoreExistsError(store_name)

    return store_name, store_path


def store_data(data_file, name=None, dtype_str=None, overwrite=False):
    """Load and parse RNG output, serialised to a local data directory

    Reads from file containing RNG output and produces a representitive pandas
    Series. The appropiate dtype is inferred from the data itself, or optionally
    from the supplied `dtype_str`.

    A name supplied or generated is used to initialise a store. If supplied,
    the name is sanitised to remove invalid characters for filepaths. If
    generated, the name will be a timestamp of initialisation.

    The representive Series is serialised using Python's pickle module, saved
    in the initialised store.

    The store's name is also written to a file in the user data directory, to
    be accessed later when identifying the last initialised store.

    Parameters
    ----------
    data_file : file-like object
        File containing RNG output
    name : `str`, optional
        Desired name of the store, which will be sanitised. If not supplied, a
        name is generated automatically.
    dtype_str : `str`, optional
        String representation of desired dtype. If not supplied, it is inferred
        from the data.
    overwrite : `bool`, default `False`
        If a name conflicts with an existing store, this decides whether to
        overwrite it.

    Raises
    ------
    TypeNotRecognizedError
        If supplied dtype_str does not recognise a dtype
    MultipleColumnsError
        If inputted data contains multiple values per line
    NameConflictError
        If attempts at generating a unique name fails
    StoreExistsError
        If a store of the same name exists already (and overwrite is set to
        `False`)

    See Also
    --------
    parse_data : Loads and parses `data_file`
    init_store : Initialises the store
    find_latest_store : Accesses the name of the last initialised store
    """
    series = parse_data(data_file, dtype_str)

    store_name, store_path = init_store(name=name, overwrite=overwrite)

    series = series.rename(store_name)

    data_path = store_path / DATA_FNAME
    pickle.dump(series, open(data_path, "wb"))

    latest_store_path = data_dir / LATEST_STORE_FNAME
    with open(latest_store_path, "w") as f:
        f.write(store_name)

    print("Data stored successfully!")


# ------------------------------------------------------------------------------
# Store interaction


class NoLatestStoreRecordedError(LookupError):
    """Error for when latest store cannot be identified"""

    def __str__(self):
        return "No record of the last initialised store was found"


def find_latest_store() -> str:
    """Find out the last initialised store

    A file is kept in the root user data directory to record the last
    initialised store's name, which this method reads to identify the store.

    Returns
    -------
    store_name : `str`
        Name of the last initialised store

    Raises
    ------
    NoLatestStoreRecordedError
        When no last initialised store is found
    """
    latest_store_path = data_dir / LATEST_STORE_FNAME
    try:
        with open(latest_store_path) as f:
            store_name = f.readlines()[0]
            if store_name in list_stores():
                return store_name
    except FileNotFoundError:
        pass

    raise NoLatestStoreRecordedError()


class StoreNotFoundError(StoreError, FileNotFoundError):
    """Error for when requested store does not exist"""

    def __str__(self):
        return f"'{self.store_name}' does not exist"


class DataNotFoundError(StoreError, FileNotFoundError):
    """Error for when requested store has no data"""

    def __str__(self):
        return f"'{self.store_name}' contains no data"


def get_data(store_name) -> pd.Series:
    """Access data of a store

    Parameters
    ----------
    store_name : `str`
        Name of the store

    Returns
    -------
    `Series`
        A pandas `Series` which represents the data

    Raises
    ------
    StoreNotFoundError
        If requested store does not exist
    DataNotFoundError
        If requested store has no data
    """
    store_path = data_dir / store_name
    if not store_path.exists():
        raise StoreNotFoundError(store_name)

    data_path = store_path / DATA_FNAME
    try:
        with open(data_path, "rb") as f:
            series = pickle.load(f)

        return series

    except FileNotFoundError:
        raise DataNotFoundError(store_name)


def drop(store_name):
    """Remove store from local data

    Parameters
    ----------
    store_name : `str`
        Name of store to remove
    """
    store_path = data_dir / store_name
    rm_tree(store_path)


def list_stores():
    """List all stores in local data"""
    try:
        for entry in scandir(data_dir):
            if entry.is_dir():
                yield entry.name

    except FileNotFoundError:
        pass


def store_result(store_name, stattest_name, result: TestResult):
    """Store result of a statistical test

    Parameters
    ----------
    store_name : `str`
        Name of store to save result in
    stattest_name : `str`
        Name of statistical test the result came from
    result : `TestResult`
        Result of the statistical test

    See Also
    --------
    store_results : Store multiple results from multiple statistical tests
    """
    with open_results(store_name) as results:
        results[stattest_name] = result


# TODO logging or warning for overwritten results
def store_results(store_name, results_dict: Dict[str, TestResult]):
    """Store results of multiple statistical tests

    Parameters
    ----------
    store_name : `str`
        Name of store to save result in
    results_dict : `Dict[str, TestResult]`
        Mapping of statistical tests to their respective results

    See Also
    --------
    store_result : Store a single results from a single statistical test
    """
    with open_results(store_name) as results:
        for stattest_name, result in results_dict.items():
            results[stattest_name] = result


@contextmanager
def open_results(store_name):
    """Context manager to read/write results of a store

    Parameters
    ----------
    store_name : `str`
        Name of store to access results in

    Yields
    ------
    results : `Dict[str, TestResult]`
        Previously stored results of statistical tests

    Raises
    ------
    StoreNotFoundError
        If requested store does not exist
    """
    store_path = data_dir / store_name

    if not store_path.exists():
        raise StoreNotFoundError

    results_path = store_path / RESULTS_FNAME

    with open_shelve(results_path) as results:
        yield results


# ------------------------------------------------------------------------------
# Helpers


def rm_tree(path: Path):
    """Recursively remove files and folders in a given directory"""
    for child in path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def open_shelve(path):
    """Adaptor of shelve.open to work with pathlib's Path"""
    path_str = str(path)

    return shelve.open(path_str)
