from itertools import product
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Union

import numpy as np
from dataclasses_json.cfg import global_config

from coinflip._patches import patch_dataclass_json_tuple_keys
from coinflip.typing import Float
from coinflip.typing import Integer

patch_dataclass_json_tuple_keys()


def int_or_float_encoder(obj):
    if np.issubdtype(type(obj), np.integer):
        return int(obj)
    else:
        return float(obj)


def list_encoder(factory: Callable):
    def func(objects: List):
        mapped_list = []
        for obj in objects:
            mapped_obj = factory(obj)
            mapped_list.append(mapped_obj)

        return mapped_list

    return func


def dict_encoder(key_factory: Callable, val_factory: Callable):
    def func(objects: Dict):
        mapped_dict = {}
        for key, val in objects.items():
            mapped_key = key_factory(key)
            mapped_val = val_factory(val)
            mapped_dict[mapped_key] = mapped_val

        return mapped_dict

    return func


atomic_encoders = {
    Integer: int,
    Float: float,
    Union[Integer, Float]: int_or_float_encoder,
}

for type_, encoder in atomic_encoders.items():
    global_config.encoders[type_] = encoder

    list_type = List[type_]
    global_config.encoders[list_type] = list_encoder(encoder)

atomic_types = atomic_encoders.keys()
for type1, type2 in product(atomic_types, atomic_types):
    dict_type = Dict[type1, type2]
    encoder1, encoder2 = atomic_encoders[type1], atomic_encoders[type2]
    global_config.encoders[dict_type] = dict_encoder(encoder1, encoder2)


bespoke_encoders = {
    Dict[Integer, DefaultDict[Tuple[Face, ...], Integer]]: dict_encoder(
        int, dict_encoder(list_encoder())
    )
}
