from dataclasses import dataclass
from functools import lru_cache
from io import StringIO
from typing import List
from typing import Tuple
from typing import Union

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from coinflip import console

__all__ = ["TestResult", "MultiTestResult", "make_testvars_table", "smartround"]


class _TestResult:
    """Representation methods for test results"""

    def __rich_console__(self, console, options):
        pass

    def print(self):
        """Prints results contents to notebook or terminal environment"""
        console.print(self)

    def __str__(self):
        # Mocks file as the stdout of a Rich Console
        buf = StringIO()
        console = Console(file=buf, force_jupyter=False)
        console.print(self)

        return buf.getvalue()


@dataclass(unsafe_hash=True)
class TestResult(_TestResult):
    """Base container for test results

    Attributes
    ----------
    statistic : ``int`` or ``float``
        Statistic of the test
    p : ``float``
        p-value of the test
    """

    statistic: Union[int, float]
    p: float

    def _results_text(self, stat_varname="statistic") -> Text:
        """``Text`` of the statistic and p-value

        Parameters
        ----------
        stat_varname : ``str``, default ``"statistic"``
            Name describing the statistic

        Returns
        -------
        ``Text``
            Multi-line Rich ``Text`` variable list
        """
        return vars_list((stat_varname, self.statistic), ("p-value", self.p))


class MultiTestResult(dict, _TestResult):
    """Base container for test results with multiple p-values

    A dictionary which pairs features of a sub-test and their respective test
    results.

    Attributes
    ----------
    statistics : ``List[Union[int, float]]``
        Statistics of the test
    pvalues : ``List[Union[int, float]]``
        p-values of the test
    min_result : ``TestResult``
        Test result with the smallest p-value
    """

    # TODO hash() is not collision resistant, so do something which is!
    def __hash__(self):
        return hash(frozenset(self.items()))

    @property
    @lru_cache()
    def statistics(self) -> List[Union[int, float]]:
        return [result.statistic for result in self.values()]

    @property
    @lru_cache()
    def pvalues(self) -> List[float]:
        return [result.p for result in self.values()]

    @property
    @lru_cache()
    def min_result(self):
        results = self.items()
        min_result = next(results)
        for result in results:
            if result.p < min_result.p:
                min_result = result

        return min_result


def make_testvars_table(*columns) -> Table:
    table = Table(box=box.SQUARE)
    table.add_column(columns[0], justify="left")
    for col in columns[1:]:
        table.add_column(col, justify="right")

    return table


def smartround(num: Union[int, float], ndigits=1) -> Union[int, float]:
    """Round number only if it's a float"""
    if isinstance(num, int):
        return int(num)
    else:
        return round(num, ndigits)


# ------------------------------------------------------------------------------
# Helpers


def vars_list(*varname_value_pairs: List[Tuple[str, Union[int, float]]]) -> Text:
    varnames, values = zip(*varname_value_pairs)

    varname_maxlen = max(len(varname) for varname in varnames)
    f_varnames = [pad_right(varname, varname_maxlen) for varname in varnames]

    f_values = align_nums(values)

    f_varname_value_pairs = [
        f_varname + "  " + f_value for f_varname, f_value in zip(f_varnames, f_values)
    ]
    return Text("\n".join(f_varname_value_pairs))


def align_nums(nums):
    f_nums = [str(smartround(num, 3)) for num in nums]

    dot_positions = []
    for f_num in f_nums:
        pos = f_num.find(".")
        if pos == -1:
            pos = len(f_num)
        dot_positions.append(pos)
    maxpos = max(dot_positions)
    f_aligned_nums = [
        " " * (maxpos - pos) + f_num for f_num, pos in zip(f_nums, dot_positions)
    ]

    return f_aligned_nums


def pad_right(string, maxlen):
    nspaces = maxlen - len(string)
    f_string = string + " " * nspaces

    return f_string
