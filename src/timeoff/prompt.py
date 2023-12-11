import sys
from datetime import datetime
from typing import Dict, List

from questionary import Style
from questionary import prompt as q_prompt


def prompt(questions: List[Dict]) -> Dict:
    style = Style(
        [
            ("separator", "fg:#cc5454"),
            ("questionmark", "fg:#673ab7 bold"),
            ("selected", "fg:#cc5454"),  # default
            ("pointer", "fg:#673ab7 bold"),
            ("instruction", ""),  # default
            ("answer", "#00FFFF bold"),
            ("question", ""),
        ],
    )
    kbi_msg = "Exiting..."
    res = q_prompt(questions, style=style, kbi_msg=kbi_msg)
    if len(res) == 0:
        sys.exit(0)
    return res


def date_validator(func):
    def wrapper(val):
        try:
            date_val = datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return "Please enter a valid date"
        return func(date_val)

    return wrapper


def float_validator(func):
    def wrapper(val):
        try:
            float_val = float(val)
        except ValueError:
            return "Please enter a valid number"
        return func(float_val)

    return wrapper


def int_validator(func):
    def wrapper(val):
        try:
            int_val = int(val)
        except ValueError:
            return "Please enter a valid number"
        return func(int_val)

    return wrapper
