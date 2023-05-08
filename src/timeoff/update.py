from datetime import datetime

from timeoff.exceptions import PolicyNotFoundError
from timeoff.models import AccruedPTO, Policy, Settings


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
    all_policies = Policy.get()

    all_accrued_pto = AccruedPTO.get()
    if len(all_accrued_pto) == 0:
        last_updated = Settings.get().starting_date
    else:
        last_updated = sorted(all_accrued_pto.keys())[-1]

    current_date = last_updated
    while current_date < datetime.today().date():
        policy = effective_policy(all_policies, current_date)
        current_date = policy.schedule.next_date(current_date)
        if current_date < datetime.today().date():
            AccruedPTO(current_date, policy.rate).save()

