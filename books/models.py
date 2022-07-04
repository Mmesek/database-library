from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from ..utils.mixins import Name, ID


class Book(SQLModel, table=True):
    isbn: str = Field(primary_key=True)
    """Book's ISBN number (Also serving as book's ID"""
    title: str
    """Title of the book"""

class Read(ID, table=True):
    book_isbn: str = Field(foreign_key="book.isbn", primary_key=True)
    start: datetime
    end: datetime
