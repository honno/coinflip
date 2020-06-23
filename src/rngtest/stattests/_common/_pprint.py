from colorama import Back
from colorama import Style
from colorama import init

__all__ = ["pretty_seq"]

init()


def pretty_seq(series, candidate):
    values = series.unique()
    if len(values) > 2:
        raise NotImplementedError()
    noncandidate = next(value for value in values if value != candidate)

    c_rep = str(candidate)[0]
    nc_rep = str(noncandidate)[0]
    if c_rep.casefold() == nc_rep.casefold():
        c_rep = "1"
        nc_rep = "0"
    series = series.map({candidate: c_rep, noncandidate: nc_rep})

    series_rep = ""
    for _, rep in series.iteritems():
        if rep == c_rep:
            colour = Back.CYAN
        else:
            colour = Back.YELLOW
        series_rep += colour + rep
    series_rep += Style.RESET_ALL

    return series_rep
