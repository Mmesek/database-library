import calendar
from datetime import datetime, timedelta

from mlib.database import ID, Base, Default as Name, Timestamp
from sqlalchemy import select
from sqlalchemy.orm import Mapped, relationship as Relationship, Session

from utils.mixins import Price as MixinPrice, Field

# from games.models import Game


CALENDAR = calendar.Calendar(firstweekday=calendar.SUNDAY)


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
    locks: Mapped[str] = Field(nullable=True)
    """List of region restrictions, if any"""
    transaction: "Transaction" = Relationship("Transaction", back_populates="key", default=None)
    platform: Mapped[str] = Field(default="Steam", nullable=False)
    """Platform this key is for"""

    def __init__(self, game_id: int, platform: str, expire: str = None) -> None:
        self.game_id = game_id
        self.platform = platform
        if expire:
            d, m, y = [int(i) for i in expire.split(".")]
            self.expire_date = datetime(y, m, d)

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


class Transaction(MixinPrice, Timestamp, Base):
    key_id: Mapped[int] = Field(primary_key=True, foreign_key="Key.id")
    """Game this transaction involves"""
    key: Key = Relationship("Key", back_populates="transaction")


class Wishlist(Timestamp, Base):
    game_id: Mapped[int] = Field(primary_key=True, foreign_key="Game.id")
    interest_scale: Mapped[int]
    played_before: Mapped[bool]
    hltb_total: Mapped[timedelta]
    hltb_story: Mapped[timedelta]


def add_bundle(session: Session, name: str, prc: float, currency: str, games: list[dict[str, tuple[str, datetime]]]):
    TODAY = datetime.now()
    NOW = TODAY.date()
    if "Choice" in name:
        year = int(name.split(" ")[-1])
        month = getattr(calendar.Month, name.split(" ")[-2].upper()).value
        monthcal = CALENDAR.monthdatescalendar(year, month)
        date = [day for week in monthcal for day in week if day.weekday() == calendar.TUESDAY and day.month == month][
            -1
        ]
    elif "Monthly" in name:
        year = int(name.split(" ")[1])
        month = getattr(calendar.Month, name.split(" ")[0].upper()).value
        monthcal = CALENDAR.monthdatescalendar(year, month)
        date = [day for week in monthcal for day in week if day.weekday() == calendar.FRIDAY and day.month == month][-1]
    else:
        date = NOW
    bundle = Bundle(
        name=name,
        price=prc,
        currency=currency,
        keys=[Key(game_id=k, platform=v[0], expire=v[1]) for k, v in games.items()] if (type(games) is dict) else games,
        date=date,
    )
    session.add(bundle)
    session.commit()
    print(
        f"Added bundle {bundle.name} with games {', '.join(game.name for game in bundle.games)} ({len(bundle.games)}) for {bundle.price} {bundle.currency} bought on {bundle.date}."
    )
