from click import echo


def frequency(series):
    counts = series.value_counts()

    echo(counts)
