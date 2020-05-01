import inspect
from functools import wraps
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location

PROFILE_KEY = "is_profile"
MULTI_PROFILE_KEY = "is_multi_profile"


def profile(func):
    @wraps(func)
    def wrapper(df):
        name = func.__name__
        series = func(df)

        series = series.rename(name)

        return name, series

    setattr(wrapper, PROFILE_KEY, True)

    return wrapper


def multi_profile(func):
    @wraps(func)
    def wrapper(df):
        name = func.__name__
        multiple_series = func(df)

        for i, series in enumerate(multiple_series):
            profile_name = name + f"_{i}"

            series = series.rename(profile_name)

            yield profile_name, series

    setattr(wrapper, MULTI_PROFILE_KEY, True)

    return wrapper


def profile_functions(functions):
    for func in functions:
        try:
            if getattr(func, PROFILE_KEY):
                yield func
        except AttributeError:
            pass


def multi_profile_functions(functions):
    for func in functions:
        try:
            if getattr(func, MULTI_PROFILE_KEY):
                yield func
        except AttributeError:
            pass


def profiled_data(df, profiles_path):
    spec = spec_from_file_location("..profiles", profiles_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    # members is a list of (function_name, function_obj) tuples
    members = inspect.getmembers(module, inspect.isfunction)
    functions = [member[1] for member in members]

    profiles = profile_functions(functions)
    for profile in profiles:
        name, series = profile(df)

        yield name, series

    multi_profiles = multi_profile_functions(functions)
    for func in multi_profiles:
        profiles = func(df)
        for name, series in profiles:

            yield name, series
