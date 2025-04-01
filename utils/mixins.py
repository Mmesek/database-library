from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass as SQLModel
from sqlalchemy import ForeignKey
# from sqlmodel import SQLModel, Field


def Field(foreign_key=None, **kwargs):
    return mapped_column(ForeignKey(foreign_key) if foreign_key else None, **kwargs)


class URL(SQLModel):
    # www
    url: Optional[str]


class PrimaryTimestamp(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.now, primary_key=True)


class Timeframe(SQLModel):
    start: Optional[datetime] = Field(default_factory=datetime.now)
    end: Optional[datetime] = Field()


class Price(SQLModel):
    price: Mapped[Decimal] = Field()
    currency: Mapped[str] = Field()


class Category(SQLModel):
    category: str
