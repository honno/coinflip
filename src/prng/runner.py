import pandas as pd

from prng.stattests.frequency import frequency

__all__ = ["run_tests"]


def cols(df):
    for col in df:
        yield df[col]


def run_tests(df, profiles):
    for profile in profiles:
        # TODO caching

        if len(df.columns) == 1:
            s = df.iloc[:, 0]
        elif profile["concat"] == "columns":
            s = pd.concat(cols(df))
        elif profile["concat"] == "rows":
            s = pd.concat(cols(df.transpose()))
        else:
            raise NotImplementedError()

        print(s)
        frequency(s)
