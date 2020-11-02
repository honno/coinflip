from functools import lru_cache
from typing import Iterable
from typing import Tuple

from rich.style import Style
from rich.table import Table
from rich.text import Text

__all__ = ["make_warning", "determine_rep", "pretty_subseq"]


warn_text = Text("WARN", style="yellow dim")


def make_warning(msg: str) -> Table:
    f_msg = Text(msg, style="dim")

    grid = Table.grid(padding=(1))
    grid.add_row(warn_text, f_msg)

    return grid


@lru_cache()
def determine_rep(heads, tails) -> Tuple[str, str]:
    """Determine single-character representations of each binary value

    Parameters
    ----------
    heads: ``Face``
        The ``1`` abstraction
    tails: ``Face``
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


bright = Style(bold=True, dim=False)


def pretty_subseq(subseq: Iterable, heads, tails) -> Text:
    """Produce a one-line pretty representation of a subsequence

    Parameters
    ----------
    subseq : ``List``
        Subsequence to represent
    heads : ``Face``
        One of the two values in ``subseq``
    tails : ``Face``
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
