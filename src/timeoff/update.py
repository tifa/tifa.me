from datetime import date, datetime

from timeoff.object.entry import Accrued
from timeoff.object.policy import Policy


def update_pto():
    for entry in forecast_accrual(date=datetime.today().date()):
        entry.save()


def forecast_accrual(date: date):
    all_accrued_pto = Accrued.get()
    last_updated = sorted(all_accrued_pto.keys())[-1]

    current_date = last_updated
    data = []
    while current_date < date:
        policy = Policy.as_of(current_date)
        current_date = policy.schedule.next_date(current_date)
        if current_date < date:
            data.append(Accrued(current_date, policy.rate))
    return data
