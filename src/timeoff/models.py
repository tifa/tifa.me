from __future__ import annotations

import json
import os
import pickle
from dataclasses import dataclass, fields
from datetime import datetime

from timeoff.config import DATA_DIR, DATA_VERSION
from timeoff.schedules import (
    Schedule,
    SemiMonthly,  # noqa: F401
)


class Data:
    @classmethod
    def _data_file(cls):
        filename = f"{cls.__name__}.pkl".lower()
        return os.path.join(DATA_DIR, str(DATA_VERSION), filename)

    @classmethod
    def _write(cls, data, mode):
        os.makedirs(os.path.dirname(cls._data_file()), exist_ok=True)
        with open(cls._data_file(), mode) as f:
            pickle.dump(json.dumps(data), f)

    @classmethod
    def _load(cls):
        if not os.path.isfile(cls._data_file()):
            return []
        with open(cls._data_file(), "rb") as f:
            data = []
            while True:
                try:
                    entry = json.loads(pickle.load(f))
                    data.append(entry)
                except EOFError:
                    break
            return data

    def save(self):
        data = {}
        for field in fields(self):
            data[field.name] = str(getattr(self, field.name))
        self._write(data, "ab")


@dataclass
class Entry(Data):
    date: datetime.date
    rate: float

    @classmethod
    def rm(cls, date):
        data = {"date": str(date), "rate": 0}
        super(cls, cls)._write(data, "ab")

    @classmethod
    def get(cls):
        data = {}
        delete = []
        for entry in super(cls, cls)._load():
            entry["date"] = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            entry["rate"] = float(entry["rate"])
            if entry["rate"] == 0:
                delete.append(entry["date"])
            else:
                data[entry["date"]] = cls(**entry)
        for date in delete:
            data.pop(date, None)

        return data


@dataclass
class Absence(Entry):
    pass


@dataclass
class AccruedPTO(Entry):
    pass


@dataclass
class Policy(Data):
    date: datetime.date
    schedule: str
    schedule_args: list
    rate: float

    @staticmethod
    def rm(date):
        data = {"date": str(date), "schedule": "", "schedule_args": [], "rate": 0}
        super(Policy, Policy)._write(data, "ab")

    @staticmethod
    def get():
        data = {}
        for entry in super(Policy, Policy)._load():
            entry["date"] = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            args = json.loads(entry["schedule_args"])
            schedule = globals()[entry["schedule"]]
            entry["schedule"] = schedule(*args)
            entry["rate"] = float(entry["rate"])
            if entry["rate"] == 0:
                entry.pop(entry["date"], None)
            else:
                data[entry["date"]] = Policy(**entry)
        return data


@dataclass
class Settings(Data):
    starting_balance: float
    starting_date: datetime.date

    @staticmethod
    def get():
        data = super(Settings, Settings)._load()[-1]
        data["starting_balance"] = float(data["starting_balance"])
        data["starting_date"] = datetime.strptime(
            data["starting_date"], "%Y-%m-%d",
        ).date()
        return Settings(**data)

