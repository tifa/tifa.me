from datetime import datetime


def date_validator(*func_args):
    func = func_args[0]
    def wrapper(*args):
        try:
            value = (datetime.strptime(args[0], "%Y-%m-%d").date(), )
        except ValueError:
            return "Please enter a valid date"
        else:
            return func(*value)
    return wrapper


def float_validator(*func_args):
    func = func_args[0]
    def wrapper(*args):
        try:
            value = (float(args[0]), )
        except ValueError:
            return "Please enter a valid number"
        else:
            return func(*value)
    return wrapper


def int_validator(*func_args):
    func = func_args[0]
    def wrapper(*args):
        try:
            value = (int(args[0]), )
        except ValueError:
            return "Please enter a valid number"
        else:
            return func(*value)
    return wrapper
