from dataclasses import dataclass


@dataclass
class Results:
    p: float

    def summary(self) -> str:
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()
