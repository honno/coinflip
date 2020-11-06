from dataclasses import dataclass
from io import StringIO
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Tuple
from typing import Union

from rich import box
from rich.console import Console
from rich.console import ConsoleRenderable
from rich.console import RenderableType
from rich.console import RenderGroup
from rich.console import render_group
from rich.measure import Measurement
from rich.measure import measure_renderables
from rich.padding import Padding
from rich.segment import Segment
from rich.table import Table
from rich.text import Text
from typing_extensions import get_args

from coinflip._randtests.common.core import make_failures_msg
from coinflip._randtests.common.pprint import make_warning
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Float
from coinflip._randtests.common.typing import Integer

__all__ = [
    "BaseTestResult",
    "TestResult",
    "MultiTestResult",
    "make_testvars_table",
    "make_chisquare_table",
    "smartround",
]


@dataclass
class BaseTestResult(ConsoleRenderable):
    heads: Face
    tails: Face
    failures: List[str]

    def _render(self) -> Iterator[RenderableType]:
        pass

    def __rich_console__(self, console, options):
        newline = Segment.line()
        *renderables, last_renderable = self.renderables

        for renderable in renderables:
            yield renderable
            yield newline
        yield last_renderable

    def __rich_measure__(self, console, max_width):
        return measure_renderables(console, self.renderables, max_width)

    @property
    def renderables(self) -> List[RenderableType]:
        renderables = list(self._render())

        if self.failures:
            msg = make_failures_msg(self.failures)
            f_failures = make_warning(msg)
            renderables.insert(0, f_failures)

        return renderables

    def print(self, **kwargs):
        """Prints results contents to notebook or terminal environment"""
        console = Console()
        console.print(self, **kwargs)

    def __str__(self):
        # Mocks file as the stdout of a Rich Console
        buf = StringIO()
        console = Console(file=buf, force_jupyter=False)
        console.print(self)

        return buf.getvalue()

    def _pretty_inputs(
        self, *name_value_pairs: Iterable[Union[Integer, Float]]
    ) -> RenderGroup:
        title = "test input"
        if len(name_value_pairs) > 1:
            title += "s"
        return make_testvars_list(title, *name_value_pairs)


class PrettyResultMixin:
    def _pretty_result(self, stat_varname="statistic", prefix=None) -> RenderGroup:
        return make_testvars_list(
            f"{prefix} result" if prefix else "result",
            (stat_varname, smartround(self.statistic)),
            ("p-value", round(self.p, 3)),
        )


@dataclass(unsafe_hash=True)
class TestResult(BaseTestResult, PrettyResultMixin):
    statistic: Union[Integer, Float]
    p: Float


@dataclass(unsafe_hash=True)
class SubTestResult(PrettyResultMixin):
    statistic: Union[Integer, Float]
    p: Float


@dataclass(unsafe_hash=True)
class MultiTestResult(BaseTestResult):
    results: Dict[Any, SubTestResult]

    # TODO lru_cache() the properties once hashing works nicely

    @property
    def statistics(self) -> List[Union[Integer, float]]:
        return [result.statistic for result in self.results.values()]

    @property
    def pvalues(self) -> List[float]:
        return [result.p for result in self.results.values()]

    @property
    def min(self):
        items = iter(self.results.items())
        min_feature, min_result = next(items)
        for feature, result in items:
            if result.p < min_result.p:
                min_feature = feature
                min_result = result

        return min_feature, min_result

    def _pretty_feature(self, result: SubTestResult) -> Text:
        pass

    def _render_sub(self, result: SubTestResult) -> Iterator[RenderableType]:
        pass

    def _results_table(self, feature_varname: str, stat_varname: str) -> Table:
        min_feature, min_result = self.min

        table = make_testvars_table(
            feature_varname, stat_varname, "p", title="sub-test results"
        )
        for feature, result in self.results.items():
            f_feature = self._pretty_feature(result)
            if feature == min_feature:
                f_feature += Text("*", style="blue")

            f_statistic = str(round(result.statistic, 3))
            f_p = str(round(result.p, 3))

            table.add_row(f_feature, f_statistic, f_p)

        min_title = Text(f"sub-test result for {feature_varname} ", style="italic")
        min_title.append(self._pretty_feature(min_result))

        f_result = Table.grid(padding=(1))
        for renderable in self._render_sub(min_result):
            f_result.add_row(renderable)

        titled_result = RenderGroup(min_title, "", f_result)

        example = Table.grid()
        example.add_row(Text.assemble(("*", "bold blue"), " "), titled_result)

        meta_table = Table.grid()
        padded_example = Padding(example, (4, 0, 0, 3))
        meta_table.add_row(table, padded_example)

        return meta_table


def make_chisquare_table(
    title: Union[str, Text],
    feature: Union[Text, str],
    classes: Iterable[Any],
    expected_occurences: Iterable[Union[Integer, float]],
    actual_occurences: Iterable[Union[Integer, float]],
    **kwargs,
) -> Table:
    f_table = make_testvars_table(
        feature, "expect", "actual", "diff", title=title, **kwargs
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
    table = OverflowTable(box=box, **kwargs)
    table.add_column(columns[0], justify="left")
    for col in columns[1:]:
        table.add_column(col, justify="right")

    return table


@render_group(fit=True)
def make_testvars_list(
    title: str, *varname_value_pairs: Tuple[str, Union[Integer, float]]
) -> RenderGroup:
    yield Text(title, style="bold")

    varnames, values = zip(*varname_value_pairs)

    varname_maxlen = max(len(varname) for varname in varnames)
    f_varnames = [pad_right(varname, varname_maxlen) for varname in varnames]

    f_values = align_nums(values)

    for f_varname, f_value in zip(f_varnames, f_values):
        yield f"  {f_varname}  {f_value}"


def smartround(num: Union[Integer, Float], ndigits=1) -> Union[int, float]:
    """Round number only if it's a float"""
    if isinstance(num, get_args(Integer)):
        return int(num)
    else:
        num = float(num)
        if num.is_integer():
            return int(num)
        else:
            return round(num, ndigits)


# ------------------------------------------------------------------------------
# Helpers


class OverflowTable(Table):
    def __init__(self, *args, title=None, caption=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.overflow_title = title
        self.overflow_caption = caption

    def __rich_console__(self, console, options):
        # TODO think about the ramifications of what I'm doing here (tests?)
        table = super().__rich_console__(console, options)

        max_width = options.max_width
        if self.width is not None:
            max_width = self.width
        if self.box:
            max_width -= len(self.columns) - 1
            if self.show_edge:
                max_width -= 2
        widths = self._calculate_column_widths(console, max_width)
        table_width = sum(widths) + self._extra_width

        render_options = options.update(width=table_width)

        def overflow_render_annotation(text: Union[str, Text], style, justify="center"):
            if isinstance(text, str):
                render_text = console.render_str(text, style=style)
            else:
                text.stylize(style)
                render_text = text

            if len(render_text) > table_width:
                return console.render(render_text, options=options)
            else:
                return console.render(
                    render_text, options=render_options.update(justify=justify)
                )

        if self.overflow_title:
            yield from overflow_render_annotation(
                self.overflow_title, "table.title", justify=self.title_justify
            )

        yield from table

        if self.overflow_caption:
            yield from overflow_render_annotation(
                self.overflow_caption, "table.caption", justify=self.caption_justify
            )

    def __rich_measure__(self, console, max_width):
        _min_width, _max_width = super().__rich_measure__(console, max_width)

        widths = [_min_width]
        if self.overflow_title:
            widths.append(len(self.overflow_title))
        if self.overflow_caption:
            widths.append(len(self.overflow_caption))

        min_width = max(widths)
        max_width = max(_max_width, min_width)

        return Measurement(min_width, max_width)


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
