from hypothesis import strategies as st


def contains_multiple_values(array):
    firstval = array[0]
    for val in array[1:]:
        if val != firstval:
            return True
    else:
        return False


def mixedbits(min_size=2):
    binary = st.integers(min_value=0, max_value=1)
    bits = st.lists(binary, min_size=min_size)
    mixedbits = bits.filter(contains_multiple_values)

    return mixedbits
