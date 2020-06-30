__all__ = ["NonBinarySequenceError", "MinimumInputError"]


class NonBinarySequenceError(ValueError):
    """Error if sequence does not contain only 2 values"""

    def __str__(self):
        return "Sequence does not contain only 2 values (i.e. binary)"


# TODO class-level message using n and min_input values
class MinimumInputError(ValueError):
    pass
