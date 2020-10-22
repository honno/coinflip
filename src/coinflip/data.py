from dataclasses import dataclass

import numpy as np
import pandas as pd

from coinflip._randtests.common.exceptions import NonBinarySequenceError

__all__ = [
    "TYPES",
    "DataParsingError",
    "parse_data",
]

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


@dataclass
class TypeNotRecognizedError(DataParsingError):
    """Error for when a given dtype string representation is not recognised"""

    dtype: str

    def __str__(self):
        f_types = ", ".join(TYPES.keys())
        return f"{self.dtype} is not a recognised data type\n" f"Valid types: {f_types}"


@dataclass
class MultipleColumnsError(DataParsingError):
    """Error for when only one column of data was expected"""

    ncols: int

    def __str__(self):
        return (
            f"Parsed data contains {self.ncols} columns, but only 1 column was expected"
        )


# TODO check for bin files
def parse_data(data_file, dtype_str=None) -> pd.Series:
    """Reads file containing data into a pandas Series

    Reads from file containing RNG output and produces a representitive pandas
    Series. The appropiate dtype is inferred from the data itself, or optionally
    from the supplied ``dtype_str``.

    Parameters
    ----------
    data_file : file-like object
        File containing RNG output
    dtype_str : ``str``, optional
        String representation of desired dtype. If not supplied, it is inferred
        from the data.

    Returns
    -------
    ``Series``
        A pandas ``Series`` which represents the data

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
    pandas.read_csv : The pandas method for reading ``data_file``
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
        except KeyError as e:
            raise TypeNotRecognizedError(dtype_str) from e

        series = series.astype(dtype)
    else:
        series = series.infer_objects()

    return series
