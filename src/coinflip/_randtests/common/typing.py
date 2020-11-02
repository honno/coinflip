from typing import Any
from typing import Union

import numpy as np

__all__ = ["Face", "Integer", "Float", "Complex", "Bool", "Void"]

Face = Any

_NumpyInt = Union[
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
_NumpyFloat = Union[np.float_, np.float16, np.float32, np.float64]
_NumpyComplex = Union[np.complex_, np.complex64, np.complex128]

Integer = Union[int, _NumpyInt]
Float = Union[float, _NumpyFloat]
Complex = Union[complex, _NumpyComplex]
Bool = Union[bool, np.bool_]
Void = Union[None, np.void]
