from dataclasses import dataclass


@dataclass
class Result:
    p: float

    def summary(self) -> str:
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()
