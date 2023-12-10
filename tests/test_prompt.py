from timeoff.prompt import date_validator, float_validator, int_validator


@date_validator
def date_func(_):
    return True


def test_date_validator_valid():
    assert date_func("2023-01-01") is True, "Validator should accept valid date"


def test_date_validator_invalid():
    assert date_func("2023-01-32") == "Please enter a valid date", "Validator should reject invalid date"


@float_validator
def float_func(_):
    return True


def test_float_validator_valid_float():
    assert float_func("123.45") is True, "Validator should accept valid float"


def test_float_validator_invalid_float():
    assert float_func("not-a-float") == "Please enter a valid number", "Validator should reject invalid float"


@int_validator
def int_func(_):
    return True


def test_int_validator_valid_int():
    assert int_func("123") is True, "Validator should accept valid integer"


def test_int_validator_invalid_int():
    assert int_func("not-an-int") == "Please enter a valid number", "Validator should reject invalid integer"
