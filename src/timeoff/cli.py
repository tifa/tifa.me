import argparse
import os
from datetime import datetime, timedelta

from tabulate import tabulate

from timeoff.config import DATA_DIR, SCHEDULES
from timeoff.models import Absence, AccruedPTO, Policy, Settings
from timeoff.prompts import date_prompt, float_prompt, int_prompt, str_prompt
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
        if not os.path.isdir(DATA_DIR):
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
        start_date = current_entry.date
        end_date = start_date
        rate = (
            current_entry.rate
            if type(current_entry) == AccruedPTO
            else (current_entry.rate * -1)
        )

        results = []
        for next_entry in it:
            if type(current_entry) == type(next_entry) \
                and current_entry.date + timedelta(days=1) == next_entry.date \
                and current_entry.rate == next_entry.rate:
                end_date = next_entry.date
            else:
                results.append((start_date, end_date, rate))
                start_date = next_entry.date
                end_date = start_date
                rate = (
                    next_entry.rate
                    if type(next_entry) == AccruedPTO
                    else (next_entry.rate * -1)
                )
            current_entry = next_entry

        results.append((start_date, end_date, rate))
        return results

    accrued_pto = list(AccruedPTO.get().values())
    absences = list(Absence.get().values())
    entries = accrued_pto + absences
    entries.sort(key=lambda x: x.date)
    entries = concat_entries(entries)

    settings = Settings.get()

    headers = ["Start", "End", "Type", "Hours", "Remaining"]

    formatted = []
    remaining = settings.starting_balance
    for entry in entries:
        num_days = (entry[1] - entry[0]).days + 1
        total_hours = entry[2] * num_days
        remaining += total_hours
        formatted.append(
            [
                entry[0],
                "-" if entry[0] == entry[1] else entry[1],
                "Accrued PTO" if entry[2] > 0 else "Vacation",
                total_hours,
                remaining,
            ],
        )
    formatted.insert(
        0, ["", "", "Initial", settings.starting_balance, settings.starting_balance],
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
    current_date = str(datetime.now().date())

    while True:
        start_date = date_prompt("Start date (YYYY-MM-DD)", current_date)
        starting_date = Settings.get().starting_date
        if start_date < starting_date:
            print(f"Date must be on or after the timeoff starting date {starting_date}")
        else:
            break

    while True:
        end_date = date_prompt("End date (YYYY-MM-DD)", str(start_date))
        if end_date < start_date:
            print("End date must be on or after the start date")
        else:
            break

    while True:
        rate = float_prompt("Hours per day", 8)
        if rate <= 0:
            print("Please enter a number greater than 0")
        else:
            break

    current_date = start_date
    while current_date <= end_date:
        Absence(current_date, rate).save()
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
    date = date_prompt("Date to remove (YYYY-MM-DD)")
    Absence.rm(date)
    print("Removed!")
    show_table()


@header
def settings_prompt():
    if os.path.isdir(DATA_DIR):
        print("Functionality to update settings and policies TBD.")
        print("If you want to start all over, delete the directory: ~/.timeoff")
        print("This will wipe out all of your data! :(")
        return

    while True:
        starting_balance = int_prompt("Starting balance (hours)", 0)
        if starting_balance < 0:
            print("Please enter a number greater than or equal to 0")
        else:
            break

    while True:
        starting_date = date_prompt("Starting date (YYYY-MM-DD)", str(datetime.now().date()))
        if starting_date > datetime.now().date():
            print("Please enter a date in the past or today")
        else:
            break

    while True:
        schedule = str_prompt("Schedule [semi-monthly]", "semi-monthly")
        if schedule in SCHEDULES:
            break
        print("Please enter a valid schedule. Available options are:")
        for schedule in SCHEDULES:
            print(f"  - {schedule}")

    args = SCHEDULES[schedule].setup_prompt()

    while True:
        rate = float_prompt("Rate (hours per period)", 2)
        if rate <= 0:
            print("Please enter a number greater than 0")
        else:
            break

    # TODO: Transactionalize
    Settings(starting_balance, starting_date).save()
    Policy(starting_date, SCHEDULES[schedule].__name__, args, rate).save()
    print("Saved!")

    update_pto()
    show_table()


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

    # Subparser for the 'settings' command
    parser_settings = subparsers.add_parser("settings", help="Manage settings")
    parser_settings.set_defaults(func=settings_prompt)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
