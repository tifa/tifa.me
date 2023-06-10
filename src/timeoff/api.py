from datetime import datetime

from timeoff.model.entry import Absence, Accrued


def get() -> list:
    combined = []
    for clazz in [Accrued, Absence]:
        combined.extend([_format_entry(entry) for _, entry in clazz.get().items()])
    return sorted(combined, key=lambda x: (x["date"], x["hours"]))


def available_hours(date=None) -> int:
    current_date = datetime.today().date()
    if date is None:
        date = current_date

    data = get()

    if date > current_date:
        from timeoff.update import forecast_accrual

        forecasted_data = [_format_entry(entry) for entry in forecast_accrual(date)]
        data.extend(forecasted_data)

        data = sorted(data, key=lambda x: (x["date"], x["hours"]))

    total_sum = 0
    for entry in data:
        if entry["date"] <= date:
            total_sum += entry["hours"]
        else:
            break

    return total_sum


def _format_entry(entry):
    clazz = entry.__class__.__name__
    return {
        "date": entry.date,
        "type": clazz,
        "hours": -entry.rate if clazz == "Absence" else entry.rate,
    }
