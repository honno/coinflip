from functools import lru_cache
from typing import Iterable
from typing import Tuple

from rich.console import RenderGroup
from rich.console import render_group
from rich.style import Style
from rich.text import Text

from coinflip._randtests.common.core import infer_faces
from coinflip._randtests.common.testutils import rawblocks

__all__ = ["determine_rep", "pretty_subseq", "pretty_sequence"]

dim = Style(dim=True)
bright = Style(bold=True, dim=False)


@lru_cache()
def determine_rep(heads, tails) -> Tuple[str, str]:
    """Determine single-character representations of each binary value

    Parameters
    ----------
    heads: ``Any``
        The ``1`` abstraction
    tails: ``Any``
        The ``0`` abstraction

    Returns
    -------
    heads_rep : ``str``
        Character representation of the ``heads``
    tails_rep : ``str``
        Character representation of the ``tails``
    """
    heads_rep = str(heads)[0]
    tails_rep = str(tails)[0]
    if heads_rep == tails_rep:
        heads_rep = "1"
        tails_rep = "0"

    return heads_rep, tails_rep


def pretty_subseq(subseq: Iterable, heads, tails) -> Text:
    """Produce a one-line pretty representation of a subsequence

    Parameters
    ----------
    subseq : ``List``
        Subsequence to represent
    heads : ``Any``
        One of the two values in ``subseq``
    tails : ``Any``
        Value in ``subseq`` which is not ``heads``

    Returns
    -------
    subseq_rep: ``Text``
        Pretty representation of ``subseq``
    """
    heads_rep, tails_rep = determine_rep(heads, tails)

    subseq_rep = ""
    for element in subseq:
        if element == heads:
            subseq_rep += heads_rep
        else:
            subseq_rep += tails_rep

    return Text(subseq_rep, style=bright)


@render_group(fit=True)
def pretty_sequence(series, ncols) -> RenderGroup:
    """Produce a multi-line representation of a sequence

    Parameters
    ----------
    series : ``Series``
        Sequence to represent
    ncols : ``int``
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
