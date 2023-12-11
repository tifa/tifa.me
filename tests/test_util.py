from timeoff.util import print_ordinal


def test_ordinal_single_digits():
    assert print_ordinal(1) == "1st"
    assert print_ordinal(2) == "2nd"
    assert print_ordinal(3) == "3rd"
    assert print_ordinal(4) == "4th"


def test_ordinal_teens():
    assert print_ordinal(11) == "11th"
    assert print_ordinal(12) == "12th"
    assert print_ordinal(13) == "13th"
    assert print_ordinal(14) == "14th"


def test_ordinal_multiples_of_ten():
    assert print_ordinal(20) == "20th"
    assert print_ordinal(30) == "30th"
    assert print_ordinal(40) == "40th"


def test_ordinal_miscellaneous():
    assert print_ordinal(21) == "21st"
    assert print_ordinal(22) == "22nd"
    assert print_ordinal(23) == "23rd"
    assert print_ordinal(24) == "24th"


def test_ordinal_high_numbers():
    assert print_ordinal(111) == "111th"
    assert print_ordinal(112) == "112th"
    assert print_ordinal(113) == "113th"
    assert print_ordinal(123) == "123rd"
