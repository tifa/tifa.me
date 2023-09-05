# timeoff 🏝

[![pypi](https://img.shields.io/pypi/v/timeoff.svg)](https://pypi.python.org/pypi/timeoff) [![license](https://img.shields.io/pypi/l/timeoff.svg)](https://pypi.python.org/pypi/timeoff) [![python](https://img.shields.io/pypi/pyversions/timeoff.svg)](https://pypi.python.org/pypi/timeoff) [![ci](https://github.com/tifa/timeoff/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/tifa/timeoff/actions/workflows/ci.yml)

Track your hours accrued and set goals and reminders to take a break!

```console
$ timeoff list

  |    o               ,---.,---.
  |--- .,-.-.,---.,---.|__. |__.
  |    || | ||---'|   ||    |
  `---'`` ' '`---'`---'`    `

  Current schedule: SemiMonthly
                    4 hours on the 1st and 15th of the month
╭────────────┬───────┬──────────┬─────────┬─────────────╮
│   Start    │  End  │   Type   │   Hours │   Remaining │
├────────────┼───────┼──────────┼─────────┼─────────────┤
│            │       │ Initial  │     100 │         100 │
│ 2023-05-12 │   -   │ Vacation │      -8 │          92 │
│ 2023-05-15 │   -   │ Accrued  │       4 │          96 │
╰────────────┴───────┴──────────┴─────────┴─────────────╯
```

## Features

- Automaticaly updates PTO hours over time.
- Define schedules to set accrued PTO rates.
- View the remaining hours of PTO available to you.

## Installation

To install ``timeoff``:

```console
$ pip install timeoff
```

## Usage

Documentation is in the works! Please run the `-h` help flag in the meantime. The interactive prompts will guide you through further instructions.

```console
$ timeoff -h
usage: timeoff [-h] {add,list,rm,settings} ...

Timeoff CLI

positional arguments:
  {add,list,rm,settings}
                        sub-command help
    add                 Add an absence
    list                List absences
    rm                  Remove an absence
    settings            Manage settings

optional arguments:
  -h, --help            show this help message and exit
```

The data is stored in `~/.timeoff`.

### Python API

You can also use this as a Python library.

Retrieve a list of all PTO hours remaining and absenses taken.

```python
import timeoff
timeoff.get()
```

Return the number of hours of PTO remaining as of today.

```python
timeoff.available_hours()
```

You can also pass in a future date to see how many hours you'll have accumulated by then.

```python
from datetime import date
timeoff.available_hours(date(2023, 9, 4))
```
