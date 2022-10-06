import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from datetime import datetime
from mlib.graphing import choose_locator, set_legend


def load_file(filename: str) -> list[datetime]:
    dates = []
    with open(filename, "r", newline="", encoding="utf-8") as file:
        lines = file.readlines()
        _data = csv.DictReader(lines[1:], lines[0].strip().split(","))

        for i in _data:
            day, month, year = [int(j) for j in i["date"].split(".")]

            try:
                dates.append(datetime(year, month, day))
            except ValueError:
                dates.append(datetime(day, month, year))

    return dates


def plot(label: str, data: list[datetime], resample: str = "D", locator: str = "Month", interval: int = 1):
    fig, ax = plt.subplots(figsize=(15, 7))
    cr = pd.Series(data, index=data)
    cr = cr.resample(resample).count()
    icr = pd.to_datetime(cr.index)

    ax.bar(icr, cr, label=label)

    lctr = choose_locator(locator, interval)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(lctr)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    set_legend(ax, "Watched", "Count", "Dates (Y/M)", framealpha=1.0)
    fig.savefig(f"{label}.png")


if __name__ == "__main__":
    plot("Movies", load_file("movies.txt"))
    plot("Episodes", load_file("episodes.txt"))
