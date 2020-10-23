import json
from typing import Callable
from typing import Mapping
from typing import Sequence
from typing import Tuple

import numpy as np
import pandas as pd


def faces(obj):
    if isinstance(obj, str):
        return obj
    else:
        return numerical(obj)


def int_(obj):
    if isinstance(obj, int):
        return obj
    else:
        return int(obj)


def float_(obj):
    if isinstance(obj, float):
        return obj
    else:
        return float(obj)


def numerical(obj):
    if isinstance(obj, (int, np.integer)):
        return int_(obj)
    else:
        return float_(obj)


def list_(factory: Callable):
    def func(objects: Sequence):
        mapped_list = []
        for obj in objects:
            mapped_obj = factory(obj)
            mapped_list.append(mapped_obj)

        return mapped_list

    return func


def tuple_(factory: Callable):
    def func(objects: Tuple):
        list_func = list_(factory)

        return tuple(list_func(objects))

    return func


def dict_(key_factory: Callable, val_factory: Callable):
    def func(objects: Mapping):
        mapped_dict = {}
        for key, val in objects.items():
            mapped_key = key_factory(key)
            mapped_val = val_factory(val)
            mapped_dict[mapped_key] = mapped_val

        return mapped_dict

    return func
