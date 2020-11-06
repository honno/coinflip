from shutil import get_terminal_size

from rich.console import RenderGroup
from rich.console import render_group
from rich.rule import Rule
from rich.style import Style
from rich.text import Text

from coinflip._randtests.common.core import infer_faces
from coinflip._randtests.common.pprint import make_warning
from coinflip._randtests.common.pprint import pretty_subseq
from coinflip._randtests.common.testutils import rawblocks
from coinflip.cli import console

__all__ = ["print_warning", "print_error", "print_series"]


err_text = Text("ERR!", style="red")


def print_error(e: Exception):
    """Pretty print exceptions"""
    text = Text(style="bright")
    text.append(err_text)
    text.append(f" {e}")

    console.print(text)


def print_warning(msg: str):
    f_warning = make_warning(msg)

    console.print(f_warning)


dim = Style(dim=True)


# TODO descriptions of the series e.g. length
def print_series(series):
    """Pretty print series that contain binary data"""
    size = get_terminal_size()
    ncols = min(size.columns, 80)

    rule = Rule("Sequence To Test", style="bright_blue")
    console.print(rule, width=ncols)

    f_series = pretty_sequence(series, ncols)
    console.print(f_series)


@render_group(fit=True)
def pretty_sequence(series, ncols) -> RenderGroup:
    """Produce a multi-line representation of a sequence

    Parameters
    ----------
    series : ``Series``
        Sequence to represent
    ncols : ``Int``
        Maximum number of characters to use per line

    Returns
    -------
    series_rep : ``RenderGroup``
        Pretty represented of a sequence
    """
    values = series.unique()
    heads, tails = infer_faces(tuple(values))

    gap = 2

    outer_w = ncols - 2 * gap
    inner_w = outer_w - 2 * gap

    pad = Text("".join(" " for _ in range(gap)))

    l_border = Text("  | ", style=dim)
    r_border = Text(" |  ", style=dim)

    l_arrow = Text(" <  ", style=dim)
    r_arrow = Text("  > ", style=dim)

    def make_hline(width) -> Text:
        return Text("+" + "".join("-" for _ in range(width - 2)) + "+", style=dim)

    def pretty_row(row) -> Text:
        return pretty_subseq(row, heads, tails)

    n = len(series)
    if n <= inner_w:
        border = pad + make_hline(n + 4) + pad

        yield border
        yield l_border + pretty_row(series.array) + r_border
        yield border

    else:
        border = pad + make_hline(outer_w) + pad
        rows = list(rawblocks(series, blocksize=inner_w, truncate=False))

        yield border
        yield l_border + pretty_row(rows[0]) + r_arrow
        yield border

        nrows = len(rows)
        if nrows <= 12:
            for row in rows[1:-1]:
                yield l_arrow + pretty_row(row) + r_arrow
                yield border

        else:
            for row in rows[1:4]:
                yield l_arrow + pretty_row(row) + r_arrow
                yield border

            omit_msg = f"..omitting {nrows - 10} rows.."
            omit_gap = ncols // 2 - len(omit_msg) // 2
            omit_pad = "".join(" " for _ in range(omit_gap))

            yield Text(omit_pad + omit_msg, style=dim)
            yield border

            for row in rows[-4:-1]:
                yield l_arrow + pretty_row(row) + r_arrow
                yield border

        yield l_arrow + pretty_row(rows[-1]) + r_border
        yield pad + make_hline(len(rows[-1]) + 2 * gap)
