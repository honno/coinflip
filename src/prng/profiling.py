import inspect
from functools import wraps
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location

PROFILE_KEY = "is_profile"

def profile(func):
    @wraps(func)
    def wrapper(df):
        name = func.__name__
        series = func(df)

        return name, series

    # TODO is some type hacking preferred here?
    setattr(wrapper, PROFILE_KEY, True)

    return wrapper


def get_profile_functions(functions):
    for function in functions:
        try:
            if getattr(function, PROFILE_KEY):
                yield function
        except AttributeError:
            pass


def get_profiled_data(df, profiles_path):
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
