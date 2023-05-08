import os

from timeoff.schedules import SemiMonthly

SCHEDULES = {
    "semi-monthly": SemiMonthly,
}

DATA_DIR = os.path.expanduser("~/.timeoff")
DATA_VERSION = 0
