from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta

from timeoff.util import print_ordinal

"""
Schedules
=========

This module contains classes that represent different accrual schedules.
"""

@dataclass
class Schedule:
    """Base class for all schedules."""

@dataclass
class PayPeriod(Schedule):
    """Base class for schedules based on pay periods."""

    MAX_WEEKDAY = 4  # Friday, 0-based index

    @abstractmethod
    def next_date(self, date):
        """Return the next date."""

    @abstractmethod
    def setup_prompt():
        """Prompt to set up the schedule. Should return a list of arguments."""

    def _next_month(self, date):
        """Return the first of next month."""
        return (date.replace(day=1) + timedelta(days=32)).replace(day=1)

    def _prev_month(self, date):
        """Return the last date of the previous month."""
        return date.replace(day=1) - timedelta(days=1)

    def _first_business_day_of_month(self, date):
        """Return the first business day of the month."""
        first_day_of_month = date.replace(day=1)
        weekday = first_day_of_month.weekday()
        if weekday > self.MAX_WEEKDAY:
            return first_day_of_month + timedelta(days=7 - weekday)
        return first_day_of_month

    def _last_business_day_of_month(self, date):
        """Return the last business day of the month."""
        last_day_of_month = self._next_month(date) - timedelta(days=1)
        weekday = last_day_of_month.weekday()
        if weekday > self.MAX_WEEKDAY:
            return last_day_of_month - timedelta(days=weekday - 4)
        return last_day_of_month


@dataclass
class SemiMonthly(PayPeriod):
    """
    A semi-monthly pay schedule.

    Examples:
        semimonthly = SemiMonthly(15, -1)
        semimonthly.next(date(2019, 1, 20)  # date(2019, 1, 31)
    """

    first: int
    second: int

    MAX_COMMON_DAY = 28  # Maximum day shared by all months in a year

    def __post_init__(self):
        """
        :param first: The first day of the month to pay on.
        :param second: The second day of the month to pay on. If second == -1,
            then it's the last day of the month."""
        if self.second != -1 and self.first >= self.second:
            msg = "The first paydate must be before the second paydate."
            raise ValueError(msg)

    def description(self):
        first_str = print_ordinal(self.first)
        second_str = "last day" if self.second == -1 else print_ordinal(self.second)
        return f"the {first_str} and {second_str} of the month"

    def next_date(self, date):
        """Return the next date either on {self.first} or {self.second} of the
        month."""

        # Next date is on the first paydate of the month.
        if date.day < self.first:
            return date.replace(day=self.first)

        # Next date is on the second (specific) paydate of the month.
        if date.day < self.second:
            return date.replace(day=self.second)

        # Next date is on the last day of the month.
        if self.second == -1:
            last_day_of_month = self._next_month(date) - timedelta(days=1)
            if date.day < last_day_of_month.day:
                return last_day_of_month

        # Next date is on the first paydate of next month.
        return self._next_month(date).replace(day=self.first)

    @staticmethod
    def setup_prompt():
        while True:
            first = input("First pay date of the month (1-28) [1]: ") or 1
            try:
                first = int(first)
            except ValueError:
                print("Please enter a valid number")
                continue

            if first < 1 or first > SemiMonthly.MAX_COMMON_DAY:
                print("Please enter a number between 1 and 28")
            else:
                break

        while True:
            second = (
                input(
                    "Second pay date of the month (2-28 or -1 for last day of the"
                    " month) [15]: ",
                )
                or 15
            )
            try:
                second = int(second)
            except ValueError:
                print("Please enter a valid number")
                continue

            if (second <= 1 or second > SemiMonthly.MAX_COMMON_DAY) and second != -1:
                print("Please enter a number between 2 and 28")
            else:
                break

        return [first, second]
