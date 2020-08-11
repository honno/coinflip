from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from io import StringIO
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

__all__ = ["TestResult", "make_testvars_table", "smartround"]


@dataclass
class TestResult:
    """Base container for test result data and subsequent representation methods

    Attributes
    ----------
    statistic : `int` or `float`
        Statistic of the test
    p : float
        p-value of the test
    """

    statistic: Union[int, float]
    p: float

    def _results_text(self, stat_varname="statistic") -> Text:
        """Returns Rich `Text` of the statistic and p-value

        Parameters
        ----------
        stat_varname : `str`, default `"statistic"`
            Name describing the statistic

        Returns
        -------
        `Text`
            Multi-line Rich `Text` variable list
        """
        return vars_list((stat_varname, self.statistic), ("p-value", self.p))

    def __rich_console__(self, console, options):
        raise NotImplementedError(
            f"No Rich representation provided for {self.__class__.__name__}"
        )

    def __str__(self):
        """Mocks stdout file as the stdout of a Rich `Console` to get `str` equivalent"""
        buf = StringIO()
        console = Console(file=buf)
        console.print(self)

        return buf.getvalue()

    def _report(self) -> Iterable[Union[str, Subplot]]:
        raise NotImplementedError(
            f"No report markup provided for {self.__class__.__name__}"
        )

    def report(self):
        """Generate report HTML

        Returns
        -------
        report : `str`
            Multi-line string of HTML markup"""
        elements = (TestResult._markup(item) for item in self._report())
        report = "".join(elements)

        return report

    @classmethod
    def _markup(cls, item):
        """Generate appropiate HTML markup for an item"""
        if isinstance(item, str):
            return f"<p>{item}</p>"

        elif isinstance(item, Subplot):
            fig = item.get_figure()

            base64 = fig2base64(fig)

            return f"<img src='data:image/svg+xml;charset=utf-8;base64, {base64}' />"

        elif isinstance(item, Figure):
            base64 = fig2base64(item)

            return f"<img src='data:image/svg+xml;charset=utf-8;base64, {base64}' />"


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


def fig2base64(fig):
    """Converts matplotlib figures to SVG as base64"""
    binary = BytesIO()
    fig.savefig(binary, format="svg")

    binary.seek(0)
    base64_bstr = b64encode(binary.read())
    base64_str = base64_bstr.decode("utf-8")

    return base64_str
