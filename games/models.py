from datetime import datetime
from sqlmodel import Field, Relationship

from ..utils.mixins import Name, ID


class Game(Name, table=True):
    achievements: list["Achievement"] = Relationship(back_populates="game")
    """List of achievements unlocked in game"""
    badges: list["Badge"] = Relationship(back_populates="game")
    """List of badges crafted for game"""
    sessions: list = Relationship(back_populates="game")
    """List of game sessions in game"""

    @property
    def playtime(self) -> float:
        """Total playtime in game"""
        return sum([i.duration for i in self.sessions])


class Achievement(Name, table=True):
    game_id: int = Field(foreign_key=Game.id, primary_key=True)
    """Game ID this achievement is for"""
    unlocked_at: datetime
    """Time when achievement was unlocked"""


class Badge(ID, table=True):
    game_id: int = Field(foreign_key=Game.id, primary_key=True)
    """Game ID this badge is for"""
    unlocked_at: datetime
    """Time when badge was crafted"""
