from sqlalchemy.orm import Mapped, relationship as Relationship, mapped_column
from sqlalchemy import Table, Column, ForeignKey, Integer
from mlib.database import SQL, ID, Timestamp, Base, Field, select
from typing import List, Optional
from dataclasses import field


class Meta(ID):
    title: Mapped[str] = Field()
    description: Mapped[str | None] = Field(default=None)  # mapped_column(nullable=True)


form_questions = Table(
    "Form_Questions",
    Base.metadata,
    Column("form_id", ForeignKey("Form.id")),
    Column("question_id", ForeignKey("Question.id")),
)


class Question(Meta, Base):
    answers: list["Answer"] = Relationship(back_populates="question", default_factory=list)
    allow_multiple_answer: Mapped[bool] = Field(default=False)


class Answer(Timestamp, ID, Base):
    user_id: Mapped[int]
    question_id: Mapped[int] = Field(foreign_key="Question.id")
    value: Mapped[str]

    question: Question = Relationship(back_populates="answers", default=None)


class Form(Meta, Base):
    questions: Mapped[List[Question]] = Relationship(secondary=form_questions, default_factory=list)
