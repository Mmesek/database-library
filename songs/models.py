from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship

from ..utils.mixins import Name, ID


class Artist_Songs(table=True):
    artist_id: int = Field(primary_key=True, foreign_key="artist.id")
    song_id: int = Field(primary_key=True, foreign_key="song.id")


class Artist(Name, table=True):
    songs: list["Song"] = Relationship(back_populates="artists", link_model=Artist_Songs)
    """Songs featuring this artist"""
    added_date: datetime
    """Date artist was \"discovered\""""


class Song(ID, table=True):
    title: str
    """Title of a song"""
    lyrics: Optional[str]
    """Song's Lyrics"""
    artists: list[Artist] = Relationship(back_populates="songs", link_model=Artist_Songs)
    """Artists featured in this song"""
    added_date: datetime
