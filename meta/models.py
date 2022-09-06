from typing import List
from sqlmodel import SQLModel, Field, Relationship
from collections import Counter
from datetime import datetime, timedelta
from ..utils.mixins import Name, URL, ID, Timestamp
from ..budget.models import Wallet


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


class User_Wallets(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.id", primary_key=True)


class User(Name):
    surname: str
    birthday: datetime
    country: str
    city: str
    street: str
    postal: str
    wallets: List[Wallet] = Relationship(link_model=User_Wallets)

    @property
    def balance(self) -> Counter:
        """Total balance across all wallets by currency"""
        c = Counter()
        for t in self.wallets:
            c.update({t.currency: t.balance})
        return c
