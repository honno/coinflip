from prng.stattests.frequency import frequency


def run_tests(df):
    s = df.iloc[:, 0]
    # TODO read spec and concat series accordingly
    # TODO multiple profiles

    frequency(s)
