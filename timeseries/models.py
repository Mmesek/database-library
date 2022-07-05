from typing import Optional
from sqlmodel import Field

from ..utils.mixins import ID, PrimaryTimestamp, Timeframe


class FoodHistory(PrimaryTimestamp, table=True):
    """Recipes prepared"""

    recipe_id: int = Field(foreign_key="recipe.id")
    """Recipe ID prepared"""


class Song_Played(PrimaryTimestamp, table=True):
    """Songs played"""

    song_id: int = Field(foreign_key="song.id")
    """Song ID that was played"""


class Read(Timeframe, ID, table=True):
    """Books read"""

    book_isbn: str = Field(foreign_key="book.isbn", primary_key=True)
    """ISBN of book that was read"""


class Watch(PrimaryTimestamp, table=True):
    """Movie/Episode watchhistory"""

    movie_id: Optional[int] = Field(foreign_key="movie.id")
    """Movie ID that was watched"""
    episode_id: Optional[int] = Field(foreign_key="episode.id")
    """Episode ID that was watched"""
    source: str
    """Where this movie/show was watched"""


class Game_Sessions(PrimaryTimestamp, table=True):
    """Game sessions"""

    game_id: int = Field(foreign_key="game.id", primary_key=True)
    """Game ID this session is for"""
    duration: float
    """Duration of game session"""
