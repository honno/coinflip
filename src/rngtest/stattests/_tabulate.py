from tabulate import tabulate as _tabulate

__all__ = ["tabulate"]


def tabulate(table, headers=(), colalign=None, **kwargs):
    """Adaptor to the tabulate.tabulate method"""
    if headers != () and colalign is None:
        colalign = ["left"]
        ncols = len(headers)
        for _ in range(ncols - 1):
            colalign.append("right")
        colalign = tuple(colalign)

    return _tabulate(table, headers=headers, colalign=colalign, **kwargs)
