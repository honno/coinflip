from functools import lru_cache

from colorama import Fore
from colorama import Style
from colorama import init

from rngtest.stattests._common import blocks

init()

__all__ = ["pretty_subseq", "pretty_seq"]


@lru_cache()
def determine_rep(candidate, noncandidate):
    c_rep = str(candidate)[0]
    nc_rep = str(noncandidate)[0]
    if c_rep.casefold() == nc_rep.casefold():
        c_rep = "1"
        nc_rep = "0"

    return c_rep, nc_rep


def pretty_subseq(series, candidate):
    values = series.unique()
    noncandidate = next(value for value in values if value != candidate)

    c_rep, nc_rep = determine_rep(candidate, noncandidate)
    series = series.map({candidate: c_rep, noncandidate: nc_rep})

    series_rep = Style.BRIGHT
    for _, rep in series.iteritems():
        if rep == c_rep:
            colour = Fore.CYAN
        else:
            colour = Fore.YELLOW
        series_rep += colour + rep
    series_rep += Style.RESET_ALL

    return series_rep


# TODO infer_candidate method
# TODO reverse blocks and other optimisations for large sequences
def pretty_seq(series, cols):
    values = series.unique()
    candidate = values[0]

    lines = []

    pad = 4
    l_border = dim("  | ")
    l_arrow = dim(" <  ")
    r_border = dim(" |  ")
    r_arrow = dim("  > ")
    outer = cols - pad
    inner = outer - pad

    def hline(width):
        return dim("+" + "".join("-" for _ in range(width - 2)) + "+")

    def pretty_row(series):
        return pretty_subseq(series, candidate)

    n = len(series)
    if n <= inner:
        border = "  " + hline(n + 4) + "  "

        lines.append(border)

        fseries = l_border + pretty_row(series) + r_border
        lines.append(fseries)

        lines.append(border)

    else:
        border = "  " + hline(outer) + "  "
        rows = list(blocks(series, blocksize=cols - 8, cutoff=False))

        lines.append(border)

        frow_first = l_border + pretty_row(rows[0]) + r_arrow
        lines.append(frow_first)
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
            lines.append(omit_pad + omit_msg)
            lines.append(border)

            for row in rows[-5:-1]:
                echo_row(row)
                lines.append(border)

        else:
            for row in rows[1:-1]:
                echo_row(row)
                lines.append(border)

        frow_last = l_arrow + pretty_row(rows[-1]) + r_border
        lines.append(frow_last)

        border_last = "  " + hline(len(rows[-1]) + pad)
        lines.append(border_last + Style.RESET_ALL)

    return "\n".join(lines)


def dim(string):
    return Style.DIM + string + Style.RESET_ALL
