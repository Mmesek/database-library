import calendar

from datetime import datetime

from decimal import Decimal
from sqlmodel import Field, Relationship

from ..utils.mixins import Name, ID, Timestamp
from ..games.models import Game

TODAY = datetime.datetime.now()
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


class Game(Game):
    """Game metadata"""

    keys: list["Key"]

    def find_bundle(self) -> "Bundle":
        i = next(filter(lambda x: not x.used, self.keys), None)
        return i.bundle if i else None

    @property
    def unused_keys(self):
        return [key.bundle for key in self.keys if not key.used]


class Bundle(Name, table=True):
    """Bundle metadata"""

    keys: list["Key"] = Relationship(back_populates="bundle")
    """Keys in this Bundle"""
    date: datetime
    """Date bundle was purchased"""
    price: Decimal
    """Price bundle was purchased for"""
    currency: str
    """Currency in which bundle was purchased"""

    def use_key(self, game: str) -> str:
        """Use key, returns key"""
        for key in self.keys:
            if key.game.name == game:
                return key.use()

    @property
    def unused_keys(self) -> list[str]:
        """Shows unused keys"""
        return [key.game.name for key in self.keys if not key.used]

    @property
    def games(self) -> list[Game]:
        """Shows bundled games"""
        return [key.game for key in self.keys]


class Key(ID, table=True):
    bundle_id: int = Field(foreign_key="bundle.id")
    """Bundle ID which this key is associated with"""
    bundle: Bundle = Relationship(back_populates="bundle.keys")
    game_id: int = Field(foreign_key="game.id")
    """Game this key unlocks"""
    game: Game = Relationship(back_populates="keys")
    platform: str = Field(default="Steam", nullable=False)
    """Platform this key is for"""
    key: str = Field(nullable=True)
    """Key"""
    used_date: datetime
    """Date when this key was used, if at all"""

    def use(self) -> str:
        self.used_date = datetime.now()
        return self.key


class Offer(Timestamp, ID, table=True):
    """Offer for this key"""

    key_id: int
    price: Decimal
    """Price for the key"""
    active: bool


class Price(Timestamp, ID, table=True):
    game_id: int = Field(primary_key=True, foreign_key="game.id")
    price: Decimal
    """Last fetched price for the game"""


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
