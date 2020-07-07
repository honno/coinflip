"""Coloured ASCII art representations of binary sequences."""
from functools import lru_cache
from typing import Tuple

from colorama import Fore
from colorama import Style

from rngtest.randtests._decorators import infer_candidate
from rngtest.randtests._testutils import blocks

__all__ = ["determine_rep", "pretty_subseq", "pretty_seq", "dim", "bright"]


@lru_cache()
def determine_rep(candidate, noncandidate) -> Tuple[str, str]:
    """Determine single-character representations of each binary value

    Parameters
    ----------
    candidate : `Any`
        One of the two values in a sequence
    noncandidate : `Any`
        Value in a sequence which is not `candidate`

    Returns
    -------
    c_rep : `str`
        Character representation of the `candidate`
    nc_rep : `str`
        Character representation of the `noncandidate`

    See Also
    --------
    lru_cache : Method used for caching results
    """
    c_rep = str(candidate)[0]
    nc_rep = str(noncandidate)[0]
    if c_rep.casefold() == nc_rep.casefold():
        c_rep = "1"
        nc_rep = "0"

    return c_rep, nc_rep


def pretty_subseq(series, candidate, noncandidate) -> str:
    """Produce a one-line pretty representation of a subsequence

    Parameters
    ----------
    series : `Series`
        Subsequence to represent
    candidate : `Any`
        One of the two values in `series`
    noncandidate : `Any`
        Value in a sequence which in `series`

    Returns
    -------
    series_rep : `str`
        Pretty representation of `series`

    See Also
    --------
    determine_rep : Method used to determine the `series` character representations
    """
    c_rep, nc_rep = determine_rep(candidate, noncandidate)
    series = series.map({candidate: c_rep, noncandidate: nc_rep})

    series_rep = ""
    for _, rep in series.iteritems():
        if rep == c_rep:
            colour = Fore.CYAN
        else:
            colour = Fore.YELLOW
        series_rep += colour + rep
    series_rep += Fore.RESET

    return bright(series_rep)


def pretty_seq(series, cols) -> str:
    """Produce a multi-line representation of a sequence

    Parameters
    ----------
    series : `Series`
        Sequence to represent
    cols : `int`
        Maximum number of characters to use per line

    Returns
    -------
    series_rep : `str`
        Pretty represented of a sequence

    See Also
    --------
    infer_candidate : Method used to infer the candidate value of the `series`
    pretty_subseq : Method wrapped to generate rows
    """
    values = series.unique()
    candidate = infer_candidate(values)
    try:
        noncandidate = next(value for value in values if value != candidate)
    except StopIteration:
        noncandidate = None

    pad = 4
    l_border = dim("  | ")
    l_arrow = dim(" <  ")
    r_border = dim(" |  ")
    r_arrow = dim("  > ")
    outer = cols - pad
    inner = outer - pad

    def pretty_row(series):
        return pretty_subseq(series, candidate, noncandidate)

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
        rows = list(blocks(series, blocksize=cols - 8, cutoff=False))

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
    string : `str`
        String to wrap

    Returns
    -------
    `str`
        Wrapped string
    """
    return Style.DIM + string + Style.RESET_ALL


def bright(string) -> str:
    """Wrap string in bright character codes

    Parameters
    ----------
    string : `str`
        String to wrap

    Returns
    -------
    `str`
        Wrapped string
    """
    return Style.BRIGHT + string + Style.RESET_ALL
