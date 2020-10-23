import copy
from dataclasses import fields

# https://github.com/lidatong/dataclasses-json/pull/251
from typing import Collection
from typing import Mapping
from typing import MutableSequence

from dataclasses_json import core


def _decode_dict_keys(key_type, xs, infer_missing):
    """
    Because JSON object keys must be strs, we need the extra step of decoding
    them back into the user's chosen python type
    """
    # handle NoneType keys... it's weird to type a Dict as NoneType keys
    # but it's valid...
    if key_type is None or key_type == Any:
        py_type = key_type = lambda x: x
    else:
        # get the constructor if using corresponding generic type in `typing`
        # otherwise fallback on constructing using type_ itself
        py_type = key_type
        try:
            py_type = _get_type_cons(key_type)
        except (TypeError, AttributeError):
            pass
    return map(py_type, _decode_items(key_type, xs, infer_missing))


def _asdict(obj, encode_json=False):
    """
    A re-implementation of `asdict` (based on the original in the `dataclasses`
    source) to support arbitrary Collection and Mapping types.
    """
    if core._is_dataclass_instance(obj):
        result = []
        for field in fields(obj):
            value = _asdict(getattr(obj, field.name), encode_json=encode_json)
            result.append((field.name, value))
        result = core._handle_undefined_parameters_safe(
            cls=obj, kvs=dict(result), usage="to"
        )
        return core._encode_overrides(
            dict(result), core._user_overrides_or_exts(obj), encode_json=encode_json
        )
    elif isinstance(obj, Mapping):
        return dict(
            (_asdict(k, encode_json=encode_json), _asdict(v, encode_json=encode_json))
            for k, v in obj.items()
        )
    elif (
        isinstance(obj, Collection)
        and not isinstance(obj, str)
        and not isinstance(obj, bytes)
    ):
        if isinstance(obj, MutableSequence):
            return list(_asdict(v, encode_json=encode_json) for v in obj)
        else:
            return tuple(_asdict(v, encode_json=encode_json) for v in obj)
    else:
        return copy.deepcopy(obj)


core._decode_dict_keys = _decode_dict_keys
core._asdict = _asdict
