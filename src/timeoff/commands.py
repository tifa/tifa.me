import argparse
from datetime import datetime, timedelta
from pathlib import Path

from tabulate import tabulate

from timeoff.config import DATA_DIR, SCHEDULES
from timeoff.object.entry import Absence, Accrued
from timeoff.object.policy import Policy
from timeoff.prompt import date_validator, float_validator, prompt
from timeoff.update import update_pto


def header(func):
    def wrapper():
        """Prompt header. Source: https://ascii.today"""
        print("")
        print("  |    o               ,---.,---.")
        print("  |--- .,-.-.,---.,---.|__. |__.")
        print("  |    || | ||---'|   ||    |")
        print("  `---'`` ' '`---'`---'`    `")
        print("")
        func()

    return wrapper


def refresh_pto(func):
    def wrapper():
        if not Path(DATA_DIR).is_dir():
            print("Please initialize by running `timeoff settings`.")
        else:
            update_pto()
            func()

    return wrapper


def show_table():
    def concat_entries(entries):
        if entries is None or len(entries) == 0:
            return []

        entries.sort(key=lambda x: x.date)
        it = iter(entries)
        current_entry = next(it, None)
        if current_entry is None:
            return []

        start_date = current_entry.date
        end_date = start_date
        rate = current_entry.rate if type(current_entry) == Accrued else (current_entry.rate * -1)

        results = []
        for next_entry in it:
            if (
                type(current_entry) == type(next_entry)
                and current_entry.date + timedelta(days=1) == next_entry.date
                and current_entry.rate == next_entry.rate
            ):
                end_date = next_entry.date
            else:
                results.append((start_date, end_date, rate))
                start_date = next_entry.date
                end_date = start_date
                rate = next_entry.rate if type(next_entry) == Accrued else (next_entry.rate * -1)
            current_entry = next_entry

        results.append((start_date, end_date, rate))
        return results

    accrued_pto = list(Accrued.get().values())
    absences = list(Absence.get().values())
    entries = accrued_pto + absences
    entries.sort(key=lambda x: x.date)
    entries = concat_entries(entries)

    headers = ["Start", "End", "Type", "Hours", "Remaining"]

    formatted = []
    remaining = 0
    for entry in entries:
        num_days = (entry[1] - entry[0]).days + 1
        total_hours = entry[2] * num_days
        remaining += total_hours
        formatted.append(
            [
                entry[0],
                "-" if entry[0] == entry[1] else entry[1],
                "Accrued" if entry[2] > 0 else "Vacation",
                total_hours,
                remaining,
            ],
        )

    policies = Policy.get()
    latest_policy_date = list(policies.keys())[-1]
    policy = policies[latest_policy_date]

    print(f"  Current schedule: {policy.schedule.__class__.__name__}")
    print(f"                    {int(policy.rate)} hours on {policy.schedule.description()}")
    print(
        tabulate(
            formatted,
            headers=headers,
            tablefmt="rounded_outline",
            colalign=("center", "center", "center", "right", "right"),
        ),
    )


@header
@refresh_pto
def add_prompt():
    current_date = datetime.now().date()
    all_accrued_pto = Accrued.get()
    starting_date = sorted(all_accrued_pto.keys())[0]

    questions = [
        {
            "type": "text",
            "name": "start_date",
            "message": "Start date (YYYY-MM-DD)",
            "default": str(current_date),
            "validate": date_validator(
                lambda val: val >= starting_date or f"Please enter a date on/after the starting date {starting_date}",
            ),
            "filter": lambda val: datetime.strptime(val, "%Y-%m-%d").date(),
        },
    ]
    answers = prompt(questions)
    questions = [
        {
            "type": "text",
            "name": "end_date",
            "message": "End date (YYYY-MM-DD)",
            "default": str(answers["start_date"]),
            "validate": date_validator(
                lambda val: val >= answers["start_date"]
                or f"Please enter a date on/after the start date {answers['start_date']}",
            ),
            "filter": lambda val: datetime.strptime(val, "%Y-%m-%d").date(),
        },
        {
            "type": "text",
            "name": "rate",
            "message": "Hours per day",
            "default": "8",
            "validate": float_validator(lambda val: val > 0 or "Please enter a number greater than 0"),
            "filter": lambda val: float(val),
        },
    ]
    answers.update(prompt(questions))

    current_date = answers["start_date"]
    while current_date <= answers["end_date"]:
        Absence(current_date, answers["rate"]).save()
        current_date += timedelta(days=1)

    print("Saved!")
    show_table()


@header
@refresh_pto
def list_prompt():
    show_table()


@header
@refresh_pto
def rm_prompt():
    questions = [
        {
            "type": "text",
            "name": "date",
            "message": "Date to remove (YYYY-MM-DD)",
            "validate": date_validator(lambda _: True),
            "filter": lambda val: datetime.strptime(val, "%Y-%m-%d").date(),
        },
    ]
    answers = prompt(questions)
    Absence.rm(answers["date"])
    print("Removed!")
    show_table()


def run_policy() -> None:
    policies = Policy.get()
    if len(policies) == 0:
        print("Add a policy:")
        return add_policy()

    list_policies()

    choices = ["Add policy", "Exit"] if len(policies) == 1 else ["Add policy", "Delete policy", "Exit"]

    questions = [
        {
            "type": "select",
            "name": "action",
            "message": "Manage policies",
            "choices": choices,
        },
    ]
    answers = prompt(questions)

    if answers["action"] == "Add policy":
        return add_policy()

    if answers["action"] == "Delete policy":
        return delete_policy()
    return None


def list_policies() -> None:
    policies = Policy.get()
    headers = ["Effective Date", "Schedule", "Description", "Rate"]
    formatted = []
    for date in policies:
        policy = policies[date]
        formatted.append([date, policy.schedule.__class__.__name__, policy.schedule.description(), policy.rate])
    print(tabulate(formatted, headers=headers, tablefmt="pretty"))


def add_policy() -> None:
    questions = [
        {
            "type": "text",
            "name": "effective_date",
            "message": "Effective date (YYYY-MM-DD)",
            "default": str(datetime.now().date()),
            "validate": date_validator(lambda _: True),
            "filter": lambda val: datetime.strptime(val, "%Y-%m-%d").date(),
        },
        {
            "type": "select",
            "name": "schedule",
            "message": "Schedule",
            "choices": SCHEDULES.keys(),
            "filter": lambda val: SCHEDULES[val],
        },
    ]
    answers = prompt(questions)
    schedule_args = answers["schedule"].setup_prompt()
    questions = [
        {
            "type": "text",
            "name": "rate",
            "message": "Rate (hours per period)",
            "default": "4",
            "validate": float_validator(lambda val: val > 0 or "Please enter a number greater than 0"),
            "filter": lambda val: float(val),
        },
    ]
    rate_answers = prompt(questions)
    answers.update(rate_answers)
    Policy(answers["effective_date"], answers["schedule"].__name__, schedule_args, answers["rate"]).save()
    print("✨ Saved!")
    return run_policy()


def delete_policy() -> None:
    questions = [
        {
            "type": "select",
            "name": "effective_date",
            "message": "Effective date",
            "choices": [str(date) for date in Policy.get()],
        },
    ]
    answers = prompt(questions)
    Policy.rm(answers["effective_date"])
    print(f"⚡️ Deleted policy from {answers['effective_date']}")
    return run_policy()


@header
def policy_prompt() -> None:
    run_policy()


def main():
    parser = argparse.ArgumentParser(description="Timeoff CLI")
    subparsers = parser.add_subparsers(help="sub-command help")

    # Subpaser for the 'add' command
    parser_add = subparsers.add_parser("add", help="Add an absence")
    parser_add.set_defaults(func=add_prompt)

    # Subparser for the 'list' command
    parser_list = subparsers.add_parser("list", help="List absences")
    parser_list.set_defaults(func=list_prompt)

    # Subparser for the 'rm' command
    parser_rm = subparsers.add_parser("rm", help="Remove an absence")
    parser_rm.set_defaults(func=rm_prompt)

    # Subparser for the 'policy' command
    policy_settings = subparsers.add_parser("policy", help="Manage policies")
    policy_settings.set_defaults(func=policy_prompt)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
