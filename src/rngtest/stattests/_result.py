from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable
from typing import Union

from matplotlib.axes import Subplot
from matplotlib.figure import Figure

from rngtest.stattests._tabulate import tabulate

__all__ = ["TestResult"]


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

    def p3f(self):
        """Returns p-value rounded to 3 decimal places

        Returns
        -------
        p : float
            p-value rounded to 3 decimal places
        """
        return round(self.p, 3)

    def stats_table(self, statname="statistic"):
        """Returns formatted table of the statistic and p-value

        Parameters
        ----------
        statname : `str`, default `"statistic"`
            Name to call the statistic

        Returns
        -------
        f_table : `str`
            Multi-line string that represents a table
        """
        if isinstance(self.statistic, float):
            f_statistic = round(self.statistic, 3)
        else:
            f_statistic = self.statistic

        table = [(statname, f_statistic), ("p-value", self.p3f())]
        f_table = tabulate(table, tablefmt="plain")

        return f_table

    def __str__(self):
        raise NotImplementedError(f"No __str__ method provided for {self.__class__.__name__}")

    def _report(self) -> Iterable[Union[str, Subplot]]:
        raise NotImplementedError(f"No report markup provided for {self.__class__.__name__}")

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


def fig2base64(fig):
    """Converts matplotlib figures to SVG as base64"""
    binary = BytesIO()
    fig.savefig(binary, format="svg")

    binary.seek(0)
    base64_bstr = b64encode(binary.read())
    base64_str = base64_bstr.decode("utf-8")

    return base64_str
