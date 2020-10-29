from typing import Any
from typing import Union

import numpy as np

__all__ = [
    "Face",
    "NumpyInteger",
    "NumpyFloat",
    "NumpyComplex",
    "Integer",
    "Float",
    "Complex",
    "Bool",
]

Face = Any

NumpyInteger = Union[
    np.int_,
    np.intc,
    np.intp,
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
]
Integer = Union[int, NumpyInteger]

NumpyFloat = Union[np.float_, np.float16, np.float32, np.float64]
Float = Union[float, NumpyFloat]

NumpyComplex = Union[np.complex_, np.complex64, np.complex128]
Complex = Union[complex, NumpyComplex]

Bool = Union[bool, np.bool_]
