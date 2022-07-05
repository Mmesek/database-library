from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    isbn: str = Field(primary_key=True)
    """Book's ISBN number (Also serving as book's ID"""
    title: str
    """Title of the book"""
