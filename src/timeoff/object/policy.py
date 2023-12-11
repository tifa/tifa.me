import datetime
import json
from dataclasses import dataclass

from timeoff.exceptions import PolicyNotFoundError
from timeoff.object.base import Model
from timeoff.object.schedule import (
    SemiMonthly,  # noqa: F401
)


@dataclass
class Policy(Model):
    date: datetime.date
    schedule: str
    schedule_args: list
    rate: float

    @staticmethod
    def rm(date):
        data = {"date": str(date), "schedule": "", "schedule_args": "[]", "rate": 0}
        super(Policy, Policy)._write(data)

    @staticmethod
    def get():
        """Return all policies."""
        data = {}
        for entry in super(Policy, Policy)._load():
            entry["date"] = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
            entry["rate"] = float(entry["rate"])
            if entry["rate"] == 0:
                data.pop(entry["date"], None)
                continue
            schedule = globals()[entry["schedule"]]
            entry["schedule"] = schedule(*json.loads(entry["schedule_args"]))
            data[entry["date"]] = Policy(**entry)
        return dict(sorted(data.items(), key=lambda item: item[0]))

    @staticmethod
    def as_of(date: datetime.date):
        """Return the policy as of a given date."""
        policies = Policy.get()
        last_policy = None
        for policy_date in sorted(policies, reverse=True):
            if policy_date <= date:
                last_policy = policies[policy_date]
            else:
                break
        if last_policy is not None:
            return last_policy
        msg = "No policy found for date."
        raise PolicyNotFoundError(msg)

    @staticmethod
    def current():
        """Return the current policy."""
        return Policy.as_of(datetime.date.today())
