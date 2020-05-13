"""Methods to enable profiling functionality

A profile is a particular view of data. Data is the DataFrame made by reading a
text file that contains RNG outputs. Profiles are Series that are made from the
data, i.e. sequences of values that are actually usable in randomness tests.
"""
import inspect
from functools import wraps
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from typing import Iterator
from typing import Tuple

import pandas as pd

# These attributes are set in the decorated functions objects
# They are used to identify profiles when loading a user-inputted script
PROFILE_KEY = "is_profile"
MULTI_PROFILE_KEY = "is_multi_profile"


def profile(func):
    """Converts methods that return a Series into profiles"""

    @wraps(func)
    def wrapper(df: pd.DataFrame) -> Tuple[str, pd.Series]:
        name = func.__name__
        series = func(df)

        series = series.rename(name)

        return name, series

    setattr(wrapper, PROFILE_KEY, True)

    return wrapper


def multi_profile(func):
    """Converts methods that return multiple Series into profiles"""

    @wraps(func)
    def wrapper(df: pd.DataFrame) -> Iterator[Tuple[str, pd.Series]]:
        name = func.__name__
        multiple_series = func(df)

        for i, series in enumerate(multiple_series):
            profile_name = name + f"_{i}"

            series = series.rename(profile_name)

            yield profile_name, series

    setattr(wrapper, MULTI_PROFILE_KEY, True)

    return wrapper


def get_profile_functions(functions):
    """Finds what methods are profiles"""
    for func in functions:
        try:
            if getattr(func, PROFILE_KEY):
                yield func
        except AttributeError:
            pass


def get_multi_profile_functions(functions):
    """Finds what methods are multi-profiles"""
    for func in functions:
        try:
            if getattr(func, MULTI_PROFILE_KEY):
                yield func
        except AttributeError:
            pass


def profiled_data(df, profiles_path) -> Iterator[Tuple[str, pd.Series]]:
    """Returns all profiles in a user-inputted profile script"""
    spec = spec_from_file_location("..profiles", profiles_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    # members is a list of (function_name, function_obj) tuples
    members = inspect.getmembers(module, inspect.isfunction)
    functions = [member[1] for member in members]

    profiles = get_profile_functions(functions)
    for profile in profiles:
        name, series = profile(df)

        yield name, series

    multi_profiles = get_multi_profile_functions(functions)
    for func in multi_profiles:
        profiles = func(df)
        for name, series in profiles:

            yield name, series
