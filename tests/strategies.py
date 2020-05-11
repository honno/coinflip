from hypothesis import strategies as st

__all__ = ["random_bits_strategy"]


def contains_multiple_values(array):
    first_value = array[0]
    for value in array[1:]:
        if value != first_value:
            return True
    else:
        return False


binary = st.integers(min_value=0, max_value=1)
bits = st.lists(binary, min_size=2)
random_bits_strategy = bits.filter(contains_multiple_values)

large_bits = st.lists(binary, min_size=100)
large_random_bits_strategy = large_bits.filter(contains_multiple_values)
