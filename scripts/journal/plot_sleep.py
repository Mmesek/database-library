import datetime
from collections import Counter

import matplotlib.pyplot as plt

from scripts.journal.tables import pair_intervals, parse as parse_table
from scripts.journal.plot import make, total
from timeseries import general as models


def trim(paired_sleep: list[models.Session], days: int):
    if days:
        paired_sleep: list[models.Session] = list(
            filter(
                lambda x: paired_sleep[-1].start - x.start < datetime.timedelta(days=days) if x.start else None,
                paired_sleep,
            )
        )
    return paired_sleep


def cut(paired_sleep: list[models.Session], days: int = 30):
    return list(
        filter(
            lambda x: paired_sleep[-1].end - x.end > datetime.timedelta(days=days) if x.end else None,
            paired_sleep,
        )
    )


def window(paired_sleep: list[models.Session], start: datetime.datetime, end: datetime.datetime):
    return list(
        filter(
            lambda x: x.start >= start and x.end <= end if x.start and x.end else None,
            paired_sleep,
        )
    )


def prepare_date_sessions(paired_sleep):
    dates = Counter()
    for day in paired_sleep:
        if day.start and day.end:
            dates[day.end.date()] += (day.end - day.start).total_seconds()
    print(f"avg sleep within 24h: {sum(dates.values()) / len(dates) / 60 / 60:.2} hours")
    return dates


def show_avg(paired_sleep: list[models.Session]):
    prepare_date_sessions(paired_sleep)
    print(
        f"avg sleep session: {(sum([(i.end - i.start).total_seconds() for i in paired_sleep if i.start and i.end]) / len(paired_sleep)) / 60/60:.2} hours"
    )


def show_longest(paired_sleep: list[models.Session]):
    longest = datetime.timedelta(seconds=0)
    date = None
    for x, s in enumerate(paired_sleep):
        if x:
            _longest = s.start - paired_sleep[x - 1].end
            if _longest > longest:
                longest = _longest
                date = s.start.date()
    print("Longest no sleep", longest, date)


def prepare() -> list[models.Session]:
    sessions, points, sleep = [], [], []
    s = set(parse_table(sessions, sleep, points))
    # print(s)
    return pair_intervals(sleep)


def save(paired_sleep: list[models.Session]):
    import csv

    with open("sleep.csv", "w", newline="", encoding="utf-8") as file:
        w = csv.writer(file)
        for sleep in paired_sleep:
            w.writerow([sleep.start, sleep.end])
    exit()


if __name__ == "__main__":
    paired_sleep = prepare()
    paired_sleep = window(paired_sleep, datetime.datetime(2024, 8, 19), datetime.datetime(2024, 9, 16))
    # paired_sleep = trim(paired_sleep, 31)

    plt.style.use("./pine.mplstyle")

    fig, ax = plt.subplots(2, 1, figsize=(20, 15))
    make(paired_sleep, fig, ax[0])  # , interval=1, resample_interval="1d")
    total(paired_sleep, fig, ax[1])
    plt.tight_layout()
    plt.savefig("sleep.png")
