from datetime import date, datetime

from timeoff.exceptions import PolicyNotFoundError
from timeoff.model.entry import Accrued
from timeoff.model.policy import Policy


def effective_policy(policies, date):
    """Return the policy in effect on the given date."""
    all_policy_dates = sorted(policies.keys())
    last = None
    for policy_date in all_policy_dates:
        if policy_date <= date:
            last = policy_date
        else:
            break
    if last is not None:
        return policies[last]
    msg = "No policy found for date."
    raise PolicyNotFoundError(msg)


def update_pto():
    for entry in forecast_accrual(date=datetime.today().date()):
        entry.save()


def forecast_accrual(date: date):
    all_policies = Policy.get()
    all_accrued_pto = Accrued.get()
    last_updated = sorted(all_accrued_pto.keys())[-1]

    current_date = last_updated
    data = []
    while current_date < date:
        policy = effective_policy(all_policies, current_date)
        current_date = policy.schedule.next_date(current_date)
        if current_date < date:
            data.append(Accrued(current_date, policy.rate))
    return data
