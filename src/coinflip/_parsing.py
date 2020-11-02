from dataclasses import dataclass

import pandas as pd

from coinflip.exceptions import DataParsingError
from coinflip.exceptions import NonBinarySequenceError

__all__ = ["parse_data"]


@dataclass
class MultipleColumnsError(DataParsingError):
    ncols: int

    def __str__(self):
        return (
            f"Parsed data contains {self.ncols} columns, but only 1 column was expected"
        )


# TODO check for bin files
def parse_data(data_file) -> pd.Series:
    df = pd.read_csv(data_file, header=None)

    ncols = len(df.columns)
    if ncols > 1:
        raise MultipleColumnsError(ncols)
    series = df.iloc[:, 0]

    if series.nunique() != 2:
        raise NonBinarySequenceError()

    series = series.infer_objects()

    return series
