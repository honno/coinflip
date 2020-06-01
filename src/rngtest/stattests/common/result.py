from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from typing import Iterable
from typing import Union

from matplotlib.axes import Subplot

__all__ = ["TestResult"]


@dataclass
class TestResult:
    statistic: Union[int, float]
    p: float

    def p3f(self):
        return round(self.p, 3)

    def __str__(self):
        raise NotImplementedError()

    def _report(self) -> Iterable[Union[str, Subplot]]:
        raise NotImplementedError()

    @classmethod
    def _markup(cls, item):
        if isinstance(item, str):
            return f"<p>{item}</p>"
        elif isinstance(item, Subplot):
            svg_bin = BytesIO()
            item.figure.savefig(svg_bin, format="svg")

            svg_bin.seek(0)
            svg_base64_bstr = b64encode(svg_bin.read())
            svg_base64_str = svg_base64_bstr.decode("utf-8")

            return f"<img src='data:image/svg+xml;charset=utf-8;base64, {svg_base64_str}' />"

    def report(self):
        elements = (TestResult._markup(item) for item in self._report())
        report = "".join(elements)

        return report
