import os
import json

from datetime import datetime, timedelta
from pathlib import Path

from mlib.utils import grouper
from timeseries import general as models

PATH = Path("data/Journal/Daily")
FOUND_CATEGORIES = set()

# TODO:
# - Parse separate points from 2022's one liners

with open("data/categories.json", "r", encoding="utf-8") as file:
    CAT = json.load(file)

with open("data/shorts.json", "r", encoding="utf-8") as file:
    TYPE_MAP = json.load(file)


def shift(point: datetime, latest_hour: int) -> datetime:
    if point.hour < latest_hour:  # and point.hour < 9:
        point += timedelta(days=1)
    # if point.hour < latest_hour and point.hour > 9:
    #    print(point, "Detected hour that's lower than highest hour")
    return point


def parse_intervals(line: str, current_day: datetime, amount: int) -> list[datetime]:
    _points = []
    last_hour = 0
    points = line.replace(" ", "-").split("-")
    if line.endswith("-") or line[0] == "":
        if len(points) % 2 != 1:
            pass
            # print("Possible error at", line, current_day.date())
    elif len(points) % 2 == 1:
        print("Possible error", list(grouper(points, 2)), current_day.date())
        breakpoint
    # elif amount % 2 == 1:
    #    print("Possible error on previous day", current_day.date())

    for x, point in enumerate(points):
        if ":" in point:
            hour, minute = point.split(":")
        else:
            hour, minute = point, 0
        if hour:
            if int(hour) > last_hour:
                last_hour = int(hour)
            delta = timedelta(hours=int(hour), minutes=int(minute))
            pt = shift(current_day + delta, last_hour)
            _points.append(pt)

    return _points


def parse_errata(line, points: list, current_day):
    x = points.pop()
    delta = line.lstrip("(").rstrip(")").lstrip("-")
    if ":" in line:
        hour, minute = delta.split(":")
    else:
        hour, minute = delta, 0
    delta = timedelta(hours=int(hour), minutes=int(minute))
    y = shift(current_day + delta, latest_hour=20)
    points.append(y)
    return models.Session(x, y, category="None", note="Errata"), points


def map_categories(desc, cday):
    t = None
    for name, aliases in TYPE_MAP["equals"].items():
        if desc in aliases:
            t = name
            break
    else:
        for name, aliases in TYPE_MAP["in"].items():
            for alias in aliases:
                if alias in desc:
                    t = name
                    break
            if t:
                break
    # print(cday, desc, t)
    return t


def parse_table_entry(line, current_day, latest_hour) -> models.Session:
    line = [i.strip() for i in line.rstrip("|").lstrip("|").split("|")]
    line.extend(["", "", "", "", ""])
    start, end, t, desc = line[:4]
    if start != "Start" and start != "-":
        if ":" in start or "-" in start:
            start_h, start_m = start.replace("!", "1").replace("-", ":").split(":")
            if not start_m:
                start_m = 0
        else:
            start_h, start_m = start or 0, 0
        if ":" in end or "-" in end:
            end_h, end_m = end.replace("!", "1").replace("-", ":").split(":")
            if not end_m:
                end_m = 0
        else:
            end_h, end_m = end or 0, 0
        if int(start_h) > latest_hour:
            latest_hour = int(start_h)
        if not t:
            t = map_categories(desc, current_day)
        else:
            t = CAT.get(t, t)
        start = current_day + timedelta(hours=int(start_h), minutes=int(start_m))
        end = current_day + timedelta(hours=int(end_h), minutes=int(end_m))
        return models.Session(
            shift(start, latest_hour),
            shift(end, latest_hour),
            note="".join(desc),
            category=t,
        )
    return


def pair_intervals(points):
    intervals = [None]
    points.sort(key=lambda x: x)
    intervals.extend(points)
    sleep = []
    for a, b in grouper(intervals, 2):
        if a and b:
            if b - a > timedelta(hours=12):
                print("Detected incredibly long sleep:", a)
            elif b - a < timedelta(minutes=3):
                print("Detected incredibly short sleep:", a)
            breakpoint
        sleep.append(models.Session(a or None, b or None, "Sleep", ""))
    return sleep


def parse_day(day: str) -> int:
    _day = day.split(" ")[0][:2]
    if not _day[-1].isdigit():
        return int(_day[:-1])
    return int(_day)


def parse(sessions, points, other):
    not_parsed = []

    for filename in os.listdir(PATH):
        year, month, day = filename.split("-")
        current_day = datetime(int(year), int(month), int(day.split(".")[0]))
        latest_hour = 0
        intervals = None

        with open(Path(PATH, filename), "r", newline="", encoding="utf-8") as file:
            for x, line in enumerate([i for i in file.read().splitlines() if i]):
                if intervals == x - 1 and line.startswith("Errata:"):
                    err, points = parse_errata(line.split(": ", 1)[-1], points, current_day)
                    sessions.append(err)
                elif (
                    line.startswith("Interval:")
                    # (line[0].isdigit() or (line.startswith("-") and line[1].isdigit()))
                    # and x <= 2
                    and not intervals
                ):
                    line = line.split(": ", 1)[1]
                    # if line.startswith("-"):
                    #    print(
                    #        current_day,
                    #        f"Interval doesn't have a start at {year}/{month}/{day}: {line}",
                    #    )
                    try:
                        points += parse_intervals(line, current_day, len(points))
                    except Exception as ex:
                        print("error", current_day, ex)
                    intervals = x
                elif "|" in line:
                    try:
                        r = parse_table_entry(line, current_day, latest_hour)
                    except Exception as ex:
                        print("error", current_day, ex)
                    if r:
                        sessions.append(r)
                        FOUND_CATEGORIES.add(sessions[-1].category)
                        latest_hour = sessions[-1].start.hour
                else:
                    if t := map_categories(line, current_day):
                        other.append(models.Point(current_day, line))
                    else:
                        not_parsed.append(line)
    return not_parsed
