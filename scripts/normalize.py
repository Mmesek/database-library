import re
import os

from datetime import datetime, timedelta
from pathlib import Path

from mlib.utils import grouper

PATH = Path("data/Journal")
OUTPUT = Path("data/Journal/Daily")

PATTERN = re.compile(r"(\d+):?(\d+)? ?- ?(\d+):?(\d+)?")
HOUR = re.compile(r"(\d\d):([!@#$%^0-9]|\d+)")
TIME = re.compile(r"(?<!\d|:)(\-)?([12]?[0-9])((?!00)[0-5]\d)(\-)?(?!\d|:)")
TIME_FMT = re.compile(r"((\d\d?):?(\d?\d?))")
DATE = re.compile(r"2\d{3}-[01]\d-[0-3]\d")
DECIMAL = re.compile(r"\.\d")
TABLE = re.compile(r"\s*\|")
RTABLE = re.compile(r"\|\s*")
COLON = re.compile(r"(\d)\;([!@#$%^0-9])")
TABLE_START = re.compile(r"(^\|? ?Start ?\|)")

LIST_ITEM = re.compile(r"- (.+?)(\(\d\d?:?\d?\d? ?-|$)")


def parse_day(day: str) -> int:
    _day = day.split(" ")[0][:2]
    if not _day[-1].isdigit():
        return int(_day[:-1])
    return int(_day)


def fmt(dt):
    s = format(dt, "%H:%M")
    h, m = s.split(":")
    if m != "00":
        h += f":{m}"
    return s


def write_missing_header():
    return ["| Start | End | T | Description |", "| - | - | - | - |"]


class Parser:
    def __init__(self, dt: datetime) -> None:
        self.dt = dt
        self.table = False
        self.metadata = False
        self.frontmatter = False
        self.frontmatter_open = False
        self.lines = []
        self._errata = None
        self._intervals = None
        self._header = False

    def write_frontmatter(self):
        return ["---", f"created: {self.dt}", "---"]

    def check_time_format(self, line: str):
        if t := TIME_FMT.match(line):
            if int(t.group(2)) > 23 or (False if not t.group(3) else int(t.group(3)) > 59):
                print("Potential error in hour code:", t.group(0), "at", self.dt.date())

    def parse_table_header(self, line: str):
        if line and self.table and not line.startswith("|"):
            if "|" not in line[1:]:
                s = line.split(" ", 2)
                if len(s) == 3:
                    s = [s[0], s[1], "", s[2]]
                line = " | ".join(s)
            line = "| " + line
        if line.endswith("| Description"):
            line += " |"
        if line.endswith("| -"):
            line += " |"
        return line

    def parse_metadata(self, line: str):
        if not self._intervals and all(
            group.isdigit() for group in line.replace("-", " ").replace(":", "").strip().split(" ")
        ):
            self._intervals = "Interval: " + line.replace(" ", "-")
            return True
        elif (
            not self._errata
            and line.strip().replace("(-", "").replace(")", "").replace("-", "").replace(":", "").isdigit()
        ):
            if line.strip().replace("-", "").replace(":", "").isdigit():
                line = "(-" + line.lstrip("-") + ")"
            self._errata = "Errata: " + line
            return True

    def save(self):
        OUTPUT.mkdir(exist_ok=True)
        with open(
            Path(OUTPUT, f"{self.dt.year}-{self.dt.month:02}-{self.dt.day:02}.md"),
            "w",
            newline="\n",
            encoding="utf-8",
        ) as file_:
            file_.write("\n".join([line for line in self.lines if line is not None]))

    def fix_timeformats(self, line: str):
        if COLON.search(line):
            line = COLON.sub(r"\1:\2", line)

        line = line.replace(":!", ":1").replace(":@", ":2").replace(":#", ":3").replace(":$", ":4").replace(":%", ":5")

        if not DATE.search(line) and not DECIMAL.search(line):
            line = TIME.sub(r"\1\2:\3\4", line)
            self.check_time_format(line)

        return line

    def fix_table_row(self, line: str):
        line = TABLE.sub(" |", line)
        line = RTABLE.sub("| ", line)
        line = line.strip()

        if TABLE_START.search(line):
            self.table = True
            line = TABLE_START.sub(r"\1", line)
            if "Description" not in line:
                line += " | Description"
        elif "|" in line and not self.table:
            self.table = True
            self._header = True

        return line

    def write_lines(self):
        if not self.frontmatter:
            self.lines = self.write_frontmatter() + self.lines

        if not self._intervals:
            print("Failed to detect intervals at", self.dt.date())
        else:
            self.group_intervals()
        self.lines.append(self._intervals)
        self.lines.append(self._errata)
        self.lines.append("")
        if self._header:
            self.lines.extend(write_missing_header())
        self.metadata = True

    def group_intervals(self):
        intervals = self._intervals.split("-")
        boilerplate, first = intervals[0].split(" ")
        intervals = [first] + [i for i in intervals[1:] if i]

        intervals = list(grouper(intervals, 2, ""))
        self._intervals = boilerplate + " " + " ".join(["-".join(interval) for interval in intervals])

    def process(self, file_lines: list[str]):
        for line in [i for i in file_lines if i]:
            if line == "---":
                self.frontmatter = True
                self.frontmatter_open = not self.frontmatter_open
            meta_line = False

            line_ = self.fix_timeformats(line)

            if line != line_:
                # print("-", line)
                # print("+", line_)
                breakpoint

            if not self.metadata and self.parse_metadata(line_):
                meta_line = True

            line_ = self.fix_table_row(line_)

            if not self.metadata and self.table:
                self.write_lines()

            if type(line_) is not list:
                line_ = self.parse_table_header(line_)

            if not meta_line:
                # if not self.table and not self.frontmatter_open and line != "---":
                #    print(line_, self.dt.date())

                if type(line_) is list:
                    self.lines.extend(line_)
                else:
                    self.lines.append(line_)
        self.save()


class ListParser(Parser):
    def fix_table_row(self, line: str):
        if line.startswith("- "):
            desc = LIST_ITEM.match(line).group(1)
            _sessions = PATTERN.findall(line)
            if not _sessions:
                line = super().fix_table_row("| | | | " + desc)
            else:
                lines = []
                for point in _sessions:
                    start = self.dt + timedelta(hours=int(point[0] or 0), minutes=int(point[1] or 0))
                    end = self.dt + timedelta(hours=int(point[2] or 0), minutes=int(point[3] or 0))

                    lines.append(super().fix_table_row(f"\n| {fmt(start.time())} | {fmt(end.time())} | | {desc}"))
                return lines
        return line


def process(path: Path, year: str, month: str, day: str):
    with open(path, "r", newline="", encoding="utf-8") as file:
        Parser(datetime(int(year), int(month), int(day))).process(file.read().splitlines())


def parse(year: str):
    for month in os.listdir(Path(PATH, year)):
        if month.endswith(".md"):
            continue
        for day in os.listdir(Path(PATH, year, month)):
            month_ = month.split(" ")[0]
            if int(month_) > 12:
                month_ = month_[1:]
            process(Path(PATH, year, month, day), year, month_, parse_day(day))


def parse_trip():
    for filename in os.listdir(Path(PATH, "Obsidian")):
        y, m, d = filename.split("-")
        d = d.split(".")[0]
        process(Path(PATH, "Obsidian", filename), y, m, d)


def parse_list(year: str):
    for filename in os.listdir(Path(PATH, year)):
        with open(Path(PATH, year, filename), "r", newline="", encoding="utf-8") as file:
            date = file.name.split(" ")[0].split("\\")[-1]
            lines = []
            for line in [i for i in file.read().splitlines()]:
                if line.startswith("#"):
                    section = line.strip("#").strip()
                    _day = parse_day(section)
                    dt = datetime(int(year), int(date), int(_day))
                    continue
                lines.append(line)
                if line == "":
                    ListParser(dt).process(lines)
                    lines = []
            if lines:
                ListParser(dt).process(lines)


parse_list("2022")
parse("2023")
parse("2024")
parse_trip()
