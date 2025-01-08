from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

# from sqlmodel import SQLModel, Field


def Field(foreign_key=None, **kwargs):
    return mapped_column(ForeignKey(foreign_key) if foreign_key else None, **kwargs)


class SQLModel:
    pass


class ID:
    # 0
    id: Mapped[int] = Field(default=None, primary_key=True)


class Name(ID, SQLModel):
    # 0 | Something
    name: Mapped[str]


class URL(SQLModel):
    # www
    url: Optional[str]


class Timestamp(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.now)


class PrimaryTimestamp(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.now, primary_key=True)


class Timeframe(SQLModel):
    start: Optional[datetime] = Field(default_factory=datetime.now)
    end: Optional[datetime]


class Price(SQLModel):
    price: Mapped[Decimal]
    currency: Mapped[str]


class Category(SQLModel):
    category: str
