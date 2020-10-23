from dataclasses import dataclass
from typing import Dict

import pandas as pd
from dataclasses_json import DataClassJsonMixin

from coinflip._randtests.common.result import BaseTestResult
from coinflip._randtests.common.result import encode
from coinflip.exceptions import DataParsingError
from coinflip.exceptions import NonBinarySequenceError

__all__ = ["parse_data", "make_report"]


@dataclass
class MultipleColumnsError(DataParsingError):
    """Error for when only one column of data was expected"""

    ncols: int

    def __str__(self):
        return (
            f"Parsed data contains {self.ncols} columns, but only 1 column was expected"
        )


# TODO check for bin files
def parse_data(data_file) -> pd.Series:
    """Reads file containing data into a pandas Series

    Reads from file containing RNG output and produces a representitive pandas
    Series. The appropiate dtype is inferred from the data itself.

    Parameters
    ----------
    data_file : file-like object
        File containing RNG output

    Returns
    -------
    ``Series``
        A pandas ``Series`` which represents the data

    Raises
    ------
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

    series = series.infer_objects()

    return series


@dataclass
class Report(DataClassJsonMixin):
    series: pd.Series = encode(pd.Series.to_json)
    results: Dict[str, BaseTestResult]


def make_report(series, results) -> Report:
    report = Report(series, results)

    return report
