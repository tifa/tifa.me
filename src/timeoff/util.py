def print_ordinal(number: int) -> str:
    """
    Return the ordinal representation of a number.

    :param number: The number to be converted.
    :type number: int
    :return: The ordinal representation of the number.
    :rtype: str
    """
    th_min_range = 10
    th_max_range = 20
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    if th_min_range <= number % 100 <= th_max_range:
        suffix = "th"
    else:
        suffix = suffixes.get(number % 10, "th")
    return f"{number}{suffix}"
