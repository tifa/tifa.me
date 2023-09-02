import json

import requests
from timeoff import available_hours

THRESHOLD_HOURS = 170
WEBHOOK_URL = "https://hooks.slack.com/services/00000000000/00000000000/000000000000000000000000"


def remind() -> None:
    hours = available_hours()
    if hours < THRESHOLD_HOURS:
        return

    payload = {"text": f"You have accrued {hours} hours of PTO"}
    response = requests.post(url=WEBHOOK_URL, data=json.dumps(payload))
    response.raise_for_status()


if __name__ == "__main__":
    remind()
