from dataclasses import dataclass


@dataclass
class TestResult:
    p: float

    def p2f(self):
        return round(self.p, 2)

    def __str__(self):
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()
