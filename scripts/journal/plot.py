import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from timeseries.general import Session


def set_legend(ax: plt.Axes):
    # Set the title and axis labels
    ax.legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, fc="orange", lw=0.5, label=">8h"),
            plt.Rectangle((0, 0), 1, 1, fc="green", lw=0.5, label="6-8h"),
            plt.Rectangle((0, 0), 1, 1, fc="blue", lw=0.5, label="1-6h"),
            plt.Rectangle((0, 0), 1, 1, fc="red", lw=0.5, label="<1h"),
        ],
        fontsize=16,
        loc="best",
        framealpha=0,
    )


def set_x(ax: plt.Axes, sessions: list[Session]):
    # Set the x-axis ticks and labels
    x_ticks = sorted(set(session.start.strftime("%Y-%m-%d") for session in sessions))
    x_labels = sorted(set(session.start.date() for session in sessions))
    ax.set_xticks(x_ticks, x_labels, minor=True, rotation="vertical")
    # ax.set_xticklabels(x_labels, rotation=90, minor=True)
    print(ax.set_xlim(-0.4, len(x_ticks)))


def set_y(ax: plt.Axes, stop: int):
    # Set the y-axis ticks and labels
    y_ticks = np.arange(0, stop, 1)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f"{hour:02d}" for hour in y_ticks])


def set_labels(ax: plt.Axes, title: str, x: str, y: str):
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)


def select_color(delta: int) -> str:
    if delta < 1:
        return "#d6211d"
    elif delta > 8:
        return "#d66d1d"
    elif delta > 6:
        return "#12a520"
    else:
        return "#1d52d6"


def get_start_end(session: Session):
    start, end = (
        session.start,
        session.end or datetime(session.start.year, session.start.month, session.start.day, 23, 59),
    )
    if not start:
        start = datetime(end.year, end.month, end.day)
        session.start = start
    if start and end:
        print(start.date(), start.time(), end.time(), end - start)
    return start, end


def make(sessions: list[Session], fig=None, ax: plt.Axes = None):
    if not ax:
        fig, ax = plt.subplots(figsize=(15, 7))

    dates = set()
    for session in sessions:
        start, end = get_start_end(session)
        date = start.strftime("%Y-%m-%d")
        dates.add(date)
        color = select_color((end - start).total_seconds() / 3600)

        if end.day > start.day or end.month > start.month:
            # Handle the case where the end datetime is on the next day
            end_date = start.date() + timedelta(days=1)
            end_date_str = end_date.strftime("%Y-%m-%d")
            ax.bar(
                date,
                (
                    timedelta(hours=24) - timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
                ).total_seconds()
                / 3600,
                bottom=start.hour + start.minute / 60,
                width=1,
                color=color,
            )
            ax.bar(
                end_date_str,
                (end - datetime(end.year, end.month, end.day)).total_seconds() / 3600,
                bottom=0,
                width=1,
                color=color,
            )
        else:
            if (end - start) < timedelta(minutes=15):
                breakpoint
            ax.bar(
                date,
                (end - start).total_seconds() / 3600,
                bottom=start.hour + start.minute / 60,
                width=1,
                color=color,
            )

    set_x(ax, sessions)

    # ax.xaxis.set_major_locator(mdates.MonthLocator())
    # ax.xaxis.set_minor_locator(mdates.DayLocator())  # 1 if len(dates) > 90 else None))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    # ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    fig.autofmt_xdate()
    set_y(ax, 25)

    set_legend(ax)

    set_labels(ax, "Sleep windows over days", "Date", "Hour")

    # Adjust the spacing and display the plot
    print(ax.set_ylim(0, top=24.05))
    # plt.subplots_adjust(bottom=0.15, left=0.05)


def total(sessions: list[Session], fig, ax: plt.Axes):
    if not ax:
        fig, ax = plt.subplots(figsize=(15, 7))

    dates = set()
    total = {}
    for session in sessions:
        start, end = get_start_end(session)
        date = start.strftime("%Y-%m-%d")
        dates.add(date)

        if end.day > start.day or end.month > start.month:
            # Handle the case where the end datetime is on the next day
            end_date = start.date() + timedelta(days=1)
            end_date_str = end_date.strftime("%Y-%m-%d")
            if date not in total:
                total[date] = 0
            total[date] += (
                timedelta(hours=24) - timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
            ).total_seconds()
            if end_date_str not in total:
                total[end_date_str] = 0
            total[end_date_str] += (end - datetime(end.year, end.month, end.day)).total_seconds()
        else:
            if (end - start) < timedelta(minutes=15):
                breakpoint
            if date not in total:
                total[date] = 0
            total[date] += (end - start).total_seconds()

    for date in total:
        delta = total[date] / 3600

        ax.bar(
            date,
            delta,
            width=1,
            color=select_color(delta),
        )

    set_x(ax, sessions)

    fig.autofmt_xdate()
    set_y(ax, 13)
    set_labels(ax, "Total sleep by day", "Date", "Hours")

    # Adjust the spacing and display the plot
    print(ax.set_ylim(0, top=12.05))
    # plt.subplots_adjust(bottom=0.15, left=0.05)
