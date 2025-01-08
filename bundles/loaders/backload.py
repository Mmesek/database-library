import calendar
from datetime import datetime
from pytz import timezone

from bundles.models import Bundle
from utils.db import make_session

CALENDAR = calendar.Calendar(firstweekday=calendar.SUNDAY)
PRICE = {
    2023: 43.55,
    2024: 40.83,
    2025: 38.79,
}


def get_date(name: str):
    if "Choice" in name:
        _year, _month = -1, -2
        _day = calendar.TUESDAY
    elif "Monthly" in name:
        _year, _month = 1, 0
        _day = calendar.FRIDAY
    else:
        return datetime.now().date()

    year = int(name.split(" ")[_year])
    month = getattr(calendar.Month, name.split(" ")[_month].upper()).value
    monthc = CALENDAR.monthdatescalendar(year, month)
    return [day for week in monthc for day in week if day.weekday() == _day and day.month == month][-1]


def new_bundle(line: str):
    name = line.split(":", 1)[0].split(" ", 1)[-1]

    bundle = Bundle(name, 0, "EUR", get_date(name), [])
    if "Choice" in bundle.name or "Monthly" in bundle.name:
        bundle.price = PRICE.get(int(bundle.name.split(" ")[-1 if "Choice" in bundle.name else 1]))
        bundle.currency = "PLN"

    return bundle


def parse(line: str):
    line = line.replace(" Treść skopiowano z Lowcygier.pl ", "").split("-")

    if len(line) == 4 and line[3].strip()[0].isdigit():
        game = line[2].strip()
    else:
        if len(line[2:]) == 2:
            game = "-".join(line[2:]).strip()
        elif len(line[2:]) > 2:
            game = f"{line[2]}-{line[3]}".strip()
        else:
            game = line[2].strip()

    expire = None
    if " < " in game:
        game, expire = game.split(" < ", 1)

        d, m, y = [int(i) for i in expire.split(".")]
        expire = datetime(y, m, d, 10, tzinfo=timezone("US/Pacific"))

    return game, "Steam", expire


if __name__ == "__main__":
    with open("games_in_bundles.txt", "r", newline="\n", encoding="utf-8") as file:
        txt = file.readlines()

    session = make_session("Keys")

    to_add = []
    bundle = None
    for line in txt:
        if line.startswith("Bundle"):
            bundle = new_bundle(line)
        elif line.startswith("-"):
            bundle.add_key(session, *parse(line))
        elif line == "\n" and bundle and bundle.games:
            to_add.append(bundle)
        elif line.strip() == "END":
            break

    to_add.reverse()
    for i in to_add:
        session.add(i)
        session.commit()
        print(
            f"Added bundle {bundle.name} with games {', '.join(game.name for game in bundle.games)} ({len(bundle.games)}) for {bundle.price} {bundle.currency} bought on {bundle.date}."
        )
