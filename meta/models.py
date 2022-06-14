from sqlmodel import SQLModel

from datetime import datetime, timedelta
from ..utils.mixins import Name, URL, ID, Timestamp


class Quote(ID, table=True):
    author: str
    """Author if this quote"""
    quote: str
    """Actual quote"""
    added_date: datetime
    """When was it added to a database"""


class Event(Timestamp, ID, table=True):
    """Wildcard event table"""
    description: str
    """Description of what this is about"""
    duration: timedelta
    """Event's Length"""


class Contact(Name, SQLModel, table=True):
    value: str


class Link(URL, Name, SQLModel, table=True):
    pass


class User(Name):
    surname: str
    birthday: datetime
    country: str
    city: str
    street: str
    postal: str
