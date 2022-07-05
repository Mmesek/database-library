from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from ..utils.mixins import Name, ID, Timestamp


class Movie(Timestamp, Name, table=True):
    pass


class Show(Name, table=True):
    pass


class Episode(Timestamp, ID, table=True):
    show_id: int = Field(foreign_key="show.id")
    season: int
    """Season of this Episode"""
    episode: int
    """Episode in a season"""
