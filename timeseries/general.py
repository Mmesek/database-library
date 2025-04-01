import datetime, enum
from dataclasses import dataclass


class Group(enum.Enum):
    Partner = 4
    Family = 3
    Friends = 2
    Strangers = 1
    Solo = 0


class Category(enum.Enum):
    Sleep = 0


class Emotion(enum.Enum):
    Other = 0


@dataclass
class Session:
    start: datetime.datetime
    end: datetime.datetime
    category: Category
    # group: Group
    # emotion: Emotion
    note: str
    # mood: int


@dataclass
class Point:
    time: datetime.datetime
    description: str
