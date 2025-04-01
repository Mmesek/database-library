from typing import Optional
from datetime import datetime
from enum import Enum

from ..utils.mixins import *

from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship

class ExperienceType(Enum):
    # It's a mess
    Other = 0
    School = 1 # Degree
    Course = 2 #
    Volunteer = 3 # Usually unpaid
    Professional = 4 #
    Open_Source = 5 # Contribution
    Commission = 6 # Paid commissioned Work
    Support = 7 # Helping out, Internship
    Hobby = 8 # Own thing
    Community = 9 # 
    Coursework = 10 # Assigment work


class Timeframe(SQLModel):
    # 2019 | 2020 | 550
    start: Optional[datetime]# = Field(default_factory=datetime.now)
    end: Optional[datetime]
    hours: Optional[float]


class Price(SQLModel):
    # 50 | EUR
    price: float
    currency: str


class Category(SQLModel):
    # Programming
    category: str


#class Base(SQLModel, table=True):
#    pass
