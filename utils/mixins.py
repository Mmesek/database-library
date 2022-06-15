from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlmodel import SQLModel, Field


class ID(SQLModel):
    # 0
    id: int = Field(primary_key=True)


class Name(ID, SQLModel):
    # 0 | Something
    name: str


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
    price: Decimal
    currency: str


class Category(SQLModel):
    category: str
