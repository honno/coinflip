from dataclasses import dataclass
from functools import lru_cache
from io import StringIO
from typing import Any
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from rich import box
from rich.console import Console
from rich.console import ConsoleRenderable
from rich.console import RenderableType
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from coinflip import console

__all__ = [
    "BaseTestResult",
    "TestResult",
    "MultiTestResult",
    "make_testvars_table",
    "make_reality_check_table",
    "vars_list",
    "smartround",
]


class BaseTestResult(ConsoleRenderable):
    """Representation methods for test results"""

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
class TestResult(BaseTestResult):
    """Base container for test results

    Attributes
    ----------
    heads: ``Any``
        The ``1`` abstraction
    tails: ``Any``
        The ``0`` abstraction
    statistic : ``int`` or ``float``
        Statistic of the test
    p : ``float``
        p-value of the test
    """

    heads: Any
    tails: Any
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


class MultiTestResult(dict, BaseTestResult):
    """Base container for test results with multiple p-values

    A dictionary which pairs features of a sub-test to their respective test
    results.

    Attributes
    ----------
    statistics : ``List[Union[int, float]]``
        Statistics of the test
    pvalues : ``List[Union[int, float]]``
        p-values of the test
    min : ``Tuple[Any, TestResult]``
        Feature of a sub-test and it's respective result with the smallest
        p-value
    """

    # TODO once testresults are figured out, don't keep this in please
    def __hash__(self):
        return 0

    @property
    @lru_cache()
    def statistics(self) -> List[Union[int, float]]:
        return [result.statistic for result in self.values()]

    @property
    @lru_cache()
    def pvalues(self) -> List[float]:
        return [result.p for result in self.values()]

    @lru_cache()
    def min(self):
        items = iter(self.items())
        min_feature, min_result = next(items)
        for feature, result in items:
            if result.p < min_result.p:
                min_feature = feature
                min_result = result

        return min_feature, min_result

    def _pretty_feature(self, result: TestResult) -> RenderableType:
        pass

    def _results_table(self, feature_varname: str, stat_varname: str) -> Table:
        min_feature, min_result = self.min()

        table = make_testvars_table(feature_varname, stat_varname, "p")
        for feature, result in self.items():
            f_feature = self._pretty_feature(result)
            if feature == min_feature:
                f_feature.stylize("on blue")

            f_statistic = str(round(result.statistic, 3))
            f_p = str(round(result.p, 3))

            table.add_row(f_feature, f_statistic, f_p)

        meta_table = Table.grid()

        example = Table.grid()
        example.add_row(Text.assemble(("*", "bold blue"), " "), min_result)

        padded_example = Padding(example, (3, 0, 0, 3))
        meta_table.add_row(table, padded_example)

        return meta_table


def make_reality_check_table(
    feature: str,
    classes: Iterable[Any],
    expected_occurences: Iterable[Union[int, float]],
    actual_occurences: Iterable[Union[int, float]],
) -> Table:
    f_table = make_testvars_table(
        feature, "expect", "actual", "diff", title=f"occurences of {feature}"
    )

    table = zip(classes, expected_occurences, actual_occurences)
    for class_, nblocks_expect, nblocks in table:
        f_class = str(class_)
        f_nblocks_expect = str(smartround(nblocks_expect))
        f_nblocks = str(nblocks)

        diff = nblocks - nblocks_expect
        f_diff = str(smartround(diff, 1))

        f_table.add_row(f_class, f_nblocks_expect, f_nblocks, f_diff)

    return f_table


def make_testvars_table(*columns, box=box.SQUARE, **kwargs) -> Table:
    table = Table(box=box, **kwargs)
    table.add_column(columns[0], justify="left")
    for col in columns[1:]:
        table.add_column(col, justify="right")

    return table


def vars_list(*varname_value_pairs: Tuple[str, Union[int, float]]) -> Text:
    varnames, values = zip(*varname_value_pairs)

    varname_maxlen = max(len(varname) for varname in varnames)
    f_varnames = [pad_right(varname, varname_maxlen) for varname in varnames]

    f_values = align_nums(values)

    f_varname_value_pairs = [
        f_varname + "  " + f_value for f_varname, f_value in zip(f_varnames, f_values)
    ]
    return Text("\n".join(f_varname_value_pairs))


def smartround(num: Union[int, float], ndigits=1) -> Union[int, float]:
    """Round number only if it's a float"""
    if isinstance(num, int):
        return int(num)
    else:
        return round(num, ndigits)


# ------------------------------------------------------------------------------
# Helpers


def align_nums(nums):
    f_nums = [str(smartround(num, 3)) for num in nums]

    dot_positions = []
    for f_num in f_nums:
        pos = f_num.find(".")
        if pos == -1:
            pos = len(f_num)
        dot_positions.append(pos)
    maxpos = max(dot_positions)

    f_aligned_nums = []
    for f_num, pos in zip(f_nums, dot_positions):
        left_pad = " " * (maxpos - pos)
        f_num = left_pad + f_num
        f_aligned_nums.append(f_num)

    return f_aligned_nums


def pad_right(string, maxlen):
    nspaces = maxlen - len(string)
    f_string = string + " " * nspaces

    return f_string
