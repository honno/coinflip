from tabulate import tabulate as _tabulate


def tabulate(table, headers=(), colalign=None, **kwargs):
    if headers != () and colalign is None:
        colalign = ["left"]
        ncols = len(headers)
        for _ in range(ncols - 1):
            colalign.append("right")
        colalign = tuple(colalign)

    return _tabulate(table, headers=headers, colalign=colalign, **kwargs)
