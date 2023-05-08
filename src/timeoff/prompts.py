from datetime import datetime


def date_prompt(prompt, default=None):
    """Prompt to set a date."""
    while True:
        if default is None:
            date = input(f"{prompt}: ")
        else:
            date = input(f"{prompt} [{default}]: ") or default
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print("Please enter a valid date")
            continue
        else:
            return date


def float_prompt(prompt, default=None):
    """Prompt to set a float."""
    while True:
        if default is None:
            value = input(f"{prompt}: ")
        else:
            value = input(f"{prompt} [{default}]: ") or default
        try:
            value = float(value)
        except ValueError:
            print("Please enter a valid number")
            continue
        else:
            return value


def int_prompt(prompt, default=None):
    """Prompt to set an int."""
    while True:
        if default is None:
            value = input(f"{prompt}: ")
        else:
            value = input(f"{prompt} [{default}]: ") or default
        try:
            value = int(value)
        except ValueError:
            print("Please enter a valid number")
            continue
        else:
            return value


def str_prompt(prompt, default=None):
    """Prompt to set a string."""
    while True:
        if default is None:
            value = input(f"{prompt}: ")
        else:
            value = input(f"{prompt} [{default}]: ") or default

        if not value:
            print("Please enter a value")
            continue

        return value
