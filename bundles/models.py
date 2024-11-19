import calendar

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, relationship as Relationship

from mlib.database import ID, Default as Name, Timestamp, Base, Field

# from ..utils.mixins import Price as MixinPrice
# from ..games.models import Game

TODAY = datetime.now()
NOW = TODAY.date()

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

c = calendar.Calendar(firstweekday=calendar.SUNDAY)


class MixinPrice:
    price: Mapped[Decimal]
    currency: Mapped[str]


class Game(Name, Base):
    """Game metadata"""

    keys: list["Key"] = Relationship("Key", back_populates="game")

    def find_bundle(self) -> "Bundle":
        i = next(filter(lambda x: not x.used, self.keys), None)
        return i.bundle if i else None

    @property
    def unused_keys(self):
        return [key.bundle for key in self.keys if not key.used_date]


class Bundle(MixinPrice, Name, Base):
    """Bundle metadata"""

    date: Mapped[datetime]
    """Date bundle was purchased"""
    keys: list["Key"] = Relationship("Key", back_populates="bundle")
    """Keys in this Bundle"""

    def use_key(self, game: str) -> str:
        """Use key, returns key"""
        for key in self.keys:
            if key.game.name == game:
                return key.use()

    @property
    def unused_keys(self) -> list[str]:
        """Shows unused keys"""
        return [key.game.name for key in self.keys if not key.used_date]

    @property
    def games(self) -> list[Game]:
        """Shows bundled games"""
        return [key.game for key in self.keys]


class Key(ID, Base):
    bundle_id: Mapped[int] = Field(foreign_key="Bundle.id")
    """Bundle ID which this key is associated with"""
    bundle: Bundle = Relationship("Bundle", back_populates="keys")
    game_id: Mapped[int] = Field(foreign_key="Game.id")
    """Game this key unlocks"""
    game: Game = Relationship("Game", back_populates="keys")
    key: Mapped[str] = Field(nullable=True)
    """Key"""
    used_date: Mapped[datetime] = Field(nullable=True)
    """Date when this key was used, if at all"""
    expire_date: Mapped[datetime] = Field(nullable=True)
    """Date when this key expires, if at all"""
    platform: Mapped[str] = Field(default="Steam", nullable=False)
    """Platform this key is for"""
    locks: Mapped[str] = Field(nullable=True)
    """List of region restrictions, if any"""

    def __init__(self, game_id: int, platform: str) -> None:
        self.game_id = game_id
        self.platform = platform

    def use(self) -> str:
        self.used_date = datetime.now()
        return self.key


class Offer(MixinPrice, Timestamp, ID, Base):
    """Offer for this key"""

    key_id: Mapped[int]
    active: Mapped[bool]


class Price(MixinPrice, Timestamp, Base):
    """Last fetched price for the game"""

    game_id: Mapped[int] = Field(primary_key=True, foreign_key="Game.id")


def add_bundle(session, name, prc, currency, games):
    if "Choice" in name:
        year = int(name.split(" ")[-1])
        month = MONTHS.get(name.split(" ")[-2])
        monthcal = c.monthdatescalendar(year, month)
        date = [day for week in monthcal for day in week if day.weekday() == calendar.TUESDAY and day.month == month][
            -1
        ]
    elif "Monthly" in name:
        year = int(name.split(" ")[1])
        month = MONTHS.get(name.split(" ")[0])
        monthcal = c.monthdatescalendar(year, month)
        date = [day for week in monthcal for day in week if day.weekday() == calendar.FRIDAY and day.month == month][-1]
    else:
        date = NOW
    bundle = Bundle(
        id=None,
        name=name,
        price=prc,
        currency=currency,
        keys=[Key(game_id=k, platform=v) for k, v in games.items()] if (type(games) is dict) else games,
        date=date,
    )
    session.add(bundle)
    session.commit()
    print(
        f"Added bundle {bundle.name} with games {', '.join(game.name for game in bundle.games)} ({len(bundle.games)}) for {bundle.price} {bundle.currency} bought on {bundle.date}."
    )
