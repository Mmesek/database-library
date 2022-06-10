from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from ..utils.mixins import Name, ID


class Movie(Name, table=True):
    release_date: datetime
    """Date when this movie was first released"""


class Show(Name, table=True):
    pass


class Episode(ID, table=True):
    show_id: int = Field(foreign_key="show.id")
    season: int
    """Season of this Episode"""
    episode: int
    """Episode in a season"""
    air_date: datetime
    """Date when this episode was first aired"""


class Watch(SQLModel, table=True):
    movie_id: Optional[int] = Field(foreign_key="movie.id")
    episode_id: Optional[int] = Field(foreign_key="episode.id")
    source: str
    """Where this movie/show was watched"""
    date: datetime
    """When was it watched"""
