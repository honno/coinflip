import pickle
from contextlib import contextmanager
from copy import copy
from datetime import datetime
from os import scandir
from pathlib import Path
from time import sleep
from typing import Dict

import numpy as np
import pandas as pd
from appdirs import AppDirs

from rngtest.slugify import slugify
from rngtest.stattests._common import TestResult
from rngtest.stattests._common.exceptions import NonBinarySequenceError

__all__ = [
    "TYPES",
    "data_dir",
    "parse_data",
    "store_data",
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
    print(f"Created store folder at {data_dir}")
except FileExistsError:
    pass

DATA_FNAME = "series.pickle"
RESULTS_FNAME = "results.pickle"

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


# TODO list valid dtype_str values using the TYPES variable
class TypeNotRecognizedError(ValueError):
    """Error for when a given dtype string representation is not recognised"""

    pass


class MultipleColumnsError(ValueError):
    """Error for when only one column of data was expected"""

    pass


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

    Parameters
    ----------
    data_file : str, path or file-like object
        File containing RNG output
    name : str, optional
        Desired name of the store, which will be sanitised. If not supplied, a
        name is generated automatically.
    dtype_str : str, optional
        String representation of desired dtype. If not supplied, it is inferred
        from the data.
    overwrite : boolean, default `False`
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
    parse_data : Method used that loads and parses `data_file`
    init_store : Method used to initialise the store
    """
    series = parse_data(data_file, dtype_str)

    store_name, store_path = init_store(name=name, overwrite=overwrite)

    series = series.rename(store_name)

    data_path = store_path / DATA_FNAME
    pickle.dump(series, open(data_path, "wb"))

    print("Data stored successfully!\n")
    print(series)


class StoreExistsError(FileExistsError):
    """Exception for when a store is being assumed to not exist but does"""

    pass


class NameConflictError(FileExistsError):
    """Error for when a unique storename could not be made"""

    pass


def parse_data(data_file, dtype_str=None) -> pd.Series:
    """Reads file containing data into a pandas Series

    Reads from file containing RNG output and produces a representitive pandas
    Series. The appropiate dtype is inferred from the data itself, or optionally
    from the supplied `dtype_str`.

    Parameters
    ----------
    data_file : str, path or file-like object
        File containing RNG output
    dtype_str : str, optional
        String representation of desired dtype. If not supplied, it is inferred
        from the data.

    Returns
    -------
    Series
        A pandas Series which represents the data

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
    store_data : Calls this method, and handles subsequent storage of data.
    """
    df = pd.read_csv(data_file, header=None)

    if len(df.columns) > 1:
        raise MultipleColumnsError()
    series = df.iloc[:, 0]

    if series.nunique() != 2:
        raise NonBinarySequenceError()

    if dtype_str is not None:
        try:
            dtype = TYPES[dtype_str]
        except KeyError:
            raise TypeNotRecognizedError()

        series = series.astype(dtype)
    else:
        series = series.infer_objects()

    return series


# TODO pretty exception printing like in tests_runner
def init_store(name=None, overwrite=False):
    """Creates store in local data

    A name supplied or generated is used to initialise a store. If supplied,
    the name is sanitised to remove invalid characters for filepaths. If
    generated, the name will be a timestamp of initialisation.

    Parameters
    ----------
    name : str, optional
        Desired name of the store, which will be sanitised. If not supplied, a
        name is generated automatically.
    overwrite : boolean, default `False`
        If a name conflicts with an existing store, this decides whether to
        overwrite it.

    Returns
    -------
    store_name : str
        Internal name of the initialised store
    store_path : Path
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
    store_data : Parses data and calls this method, to then save data in store.
    """
    if name is not None:
        store_name = slugify(name)

        if store_name != name:
            print(f"Store name {name} encoded as {store_name}")

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
            raise NameConflictError()

        print(f"Store name to be encoded as {store_name}")

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


# ------------------------------------------------------------------------------
# Store interaction


class StoreNotFoundError(FileNotFoundError):
    """Error for when requested store does not exist"""

    pass


class DataNotFoundError(LookupError):
    """Error for when requested store has no data"""

    pass


def get_data(store_name) -> pd.Series:
    """Access data of a store

    Parameters
    ----------
    store_name : str
        Name of the store

    Returns
    -------
    Series
        A pandas Series which represents the data

    Raises
    ------
    StoreNotFoundError
        If requested store does not exist
    DataNotFoundError
        If requested store has no data
    """
    store_path = data_dir / store_name
    if not store_path.exists():
        raise StoreNotFoundError()

    data_path = store_path / DATA_FNAME
    try:
        with open(data_path, "rb") as f:
            series = pickle.load(f)

        return series

    except FileNotFoundError:
        raise DataNotFoundError()


def drop(store_name):
    """Remove store from local data

    Parameters
    ----------
    store_name : str
        Name of store to remove
    """
    store_path = data_dir / store_name
    rm_tree(store_path)


def list_stores():
    """List all stores in local data"""
    try:
        for f in scandir(data_dir):
            if f.is_dir():
                yield f.name

    except FileNotFoundError:
        pass


def store_result(store_name, stattest_name, result: TestResult):
    """Store result of a statistical test

    Parameters
    ----------
    store_name : str
        Name of store to save result in
    stattest_name : str
        Name of statistical test the result came from
    result : TestResult
        Result of the statistical test

    See Also
    --------
    store_results : Store multiple results from multiple statistical tests
    """
    with open_results(store_name, write=True) as results:
        results[stattest_name] = result


# TODO logging or warning for overwritten results
def store_results(store_name, results_dict: Dict[str, TestResult]):
    """Store results of multiple statistical tests

    Parameters
    ----------
    store_name : str
        Name of store to save result in
    results_dict : Dict[str, TestResult]
        Mapping of statistical tests to their respective results

    See Also
    --------
    store_result : Store a single results from a single statistical test
    """
    with open_results(store_name, write=True) as results:
        for stattest_name, result in results_dict.items():
            results[stattest_name] = result


class ChangesNotSavedWarning(UserWarning):
    """Warning for when changes made to object which will not be saved"""

    pass


@contextmanager
def open_results(store_name, write=False):
    """Context manager to open results of a store

    Parameters
    ----------
    store_name : str
        Name of store to access results in
    write : bool, default `False`
        Whether to save changes to modified `results`

    Yields
    ------
    results : Dict[str, TestResult]
        Previously stored results of statistical tests

    Raises
    ------
    ChangesNotSavedWarning
        If `results` is modified but write is set to `False`
    """
    store_path = data_dir / store_name
    results_path = store_path / RESULTS_FNAME

    if not results_path.exists():
        results = {}
    else:
        with open(results_path, "rb") as f:
            try:
                results = pickle.load(f)
            except EOFError:
                results = {}

    results_old = copy(results)

    if not write:
        with open(results_path, "rb") as f:
            yield results

        if results is not results_old:
            raise ChangesNotSavedWarning()

    else:
        with open(results_path, "wb") as f:
            yield results

            if results is not results_old:
                pickle.dump(results, f)


# ------------------------------------------------------------------------------
# Helpers


def rm_tree(path: Path):
    """Recursively remove files and folders in a given directory

    Parameters
    ----------
    path : Path
        Where to recursively remove files in
    """
    for child in path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()
