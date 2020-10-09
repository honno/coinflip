"""Coloured ASCII art representations of binary sequences."""
from functools import lru_cache
from typing import Tuple

from colorama import Style

from coinflip._randtests.testutils import blocks
from coinflip._randtests.testutils import infer_faces

__all__ = ["determine_rep", "pretty_subseq", "pretty_seq", "dim", "bright"]


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


def pretty_subseq(series, heads, tails) -> str:
    """Produce a one-line pretty representation of a subsequence

    Parameters
    ----------
    series : ``Series``
        Subsequence to represent
    heads : ``Any``
        One of the two values in ``series``
    tails : ``Any``
        Value in ``series`` which is not ``heads``

    Returns
    -------
    series_rep : ``str``
        Pretty representation of ``series``

    See Also
    --------
    determine_rep : Method used to determine the ``series`` character representations
    """
    heads_rep, tails_rep = determine_rep(heads, tails)
    series = series.map({heads: heads_rep, tails: tails_rep})

    series_rep = "".join(rep for _, rep in series.items())

    return bright(series_rep)


def pretty_seq(series, cols) -> str:
    """Produce a multi-line representation of a sequence

    Parameters
    ----------
    series : ``Series``
        Sequence to represent
    cols : ``int``
        Maximum number of characters to use per line

    Returns
    -------
    series_rep : ``str``
        Pretty represented of a sequence

    See Also
    --------
    infer_faces : Method used to infer the `heads` and `tails` of the ``series``
    pretty_subseq : Method wrapped to generate rows
    """
    values = series.unique()
    heads, tails = infer_faces(tuple(values))

    pad = 4
    l_border = dim("  | ")
    l_arrow = dim(" <  ")
    r_border = dim(" |  ")
    r_arrow = dim("  > ")
    outer = cols - pad
    inner = outer - pad

    def pretty_row(series):
        return pretty_subseq(series, heads, tails)

    lines = []

    n = len(series)
    if n <= inner:
        border = "  " + hline(n + 4) + "  "

        lines.append(border)

        f_series = l_border + pretty_row(series) + r_border
        lines.append(f_series)

        lines.append(border)

    else:
        border = "  " + hline(outer) + "  "
        rows = list(blocks(series, blocksize=cols - 8, truncate=False))

        lines.append(border)

        f_row_first = l_border + pretty_row(rows[0]) + r_arrow
        lines.append(f_row_first)
        lines.append(border)

        def echo_row(row):
            frow = l_arrow + pretty_row(row) + r_arrow
            lines.append(frow)

        nrows = len(rows)
        if nrows > 10:
            for row in rows[1:5]:
                echo_row(row)
                lines.append(border)

            omit_msg = dim(f"..omitting {nrows - 10} rows..")
            omit_pad = "".join(" " for _ in range((cols // 2) - (len(omit_msg) // 2)))
            f_omit = omit_pad + omit_msg
            lines.append(f_omit)
            lines.append(border)

            for row in rows[-5:-1]:
                echo_row(row)
                lines.append(border)

        else:
            for row in rows[1:-1]:
                echo_row(row)
                lines.append(border)

        f_row_last = l_arrow + pretty_row(rows[-1]) + r_border
        lines.append(f_row_last)

        border_last = "  " + hline(len(rows[-1]) + pad)
        lines.append(border_last + Style.RESET_ALL)

    return "\n".join(lines)


def hline(width) -> str:
    """Construct a horizontal line string"""
    return dim("+" + "".join("-" for _ in range(width - 2)) + "+")


def dim(string) -> str:
    """Wrap string in dim character codes

    Parameters
    ----------
    string : ``str``
        String to wrap

    Returns
    -------
    ``str``
        Wrapped string
    """
    return Style.DIM + string + Style.RESET_ALL


def bright(string) -> str:
    """Wrap string in bright character codes

    Parameters
    ----------
    string : ``str``
        String to wrap

    Returns
    -------
    ``str``
        Wrapped string
    """
    return Style.BRIGHT + string + Style.RESET_ALL
