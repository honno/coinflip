from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable
from typing import Union

from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from tabulate import tabulate

__all__ = ["TestResult"]


@dataclass
class TestResult:
    statistic: Union[int, float]
    p: float

    def p3f(self):
        return round(self.p, 3)

    def stats_table(self, statname="statistic"):
        if isinstance(self.statistic, float):
            f_statistic = round(self.statistic, 3)
        else:
            f_statistic = self.statistic

        table = [(statname, f_statistic), ("p-value", self.p3f())]
        f_table = tabulate(table, tablefmt="plain")

        return f_table

    def __str__(self):
        raise NotImplementedError()

    def _report(self) -> Iterable[Union[str, Subplot]]:
        raise NotImplementedError()

    def report(self):
        elements = (TestResult._markup(item) for item in self._report())
        report = "".join(elements)

        return report

    @classmethod
    def _markup(cls, item):
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
    binary = BytesIO()
    fig.savefig(binary, format="svg")

    binary.seek(0)
    base64_bstr = b64encode(binary.read())
    base64_str = base64_bstr.decode("utf-8")

    return base64_str
