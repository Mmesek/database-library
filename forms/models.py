from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship as Relationship, mapped_column as Field
from mlib.database import ID, Timestamp, Base
from datetime import datetime
from uuid import UUID


class Meta(ID):
    title: Mapped[str] = Field()
    """Title, or a question of this field"""
    description: Mapped[str | None] = Field(default=None)
    """Optional description for this field"""


class Form(Meta, Base):
    """Form metadata"""

    # questions: Mapped[list["Question"]] = Relationship(secondary="Form_Questions", default_factory=list)

    # question: "Question" = Relationship(back_populates="answers", default=None)


class Form_Questions(Base):
    """Association of questions to a specific form"""

    form_id: Mapped[int] = Field(ForeignKey("Form.id"), primary_key=True)
    """Form this question is associated with"""
    question_id: Mapped[int] = Field(ForeignKey("Question.id"), primary_key=True)
    """Associated Question"""
    required: Mapped[bool] = Field(default=False)
    """Whether this question is mandatory in this form"""


class Question(Meta, Base):
    """Question data"""

    # answers: list["Answer"] = Relationship(back_populates="question", default_factory=list)
    type: Mapped[str] = Field(default=None, nullable=False)
    """Type of this question, for example Text, Select or Choice"""
    allow_multiple_answer: Mapped[bool] = Field(default=False)
    """Whether to allow multiple answers for this question"""
    min_length: Mapped[int | None] = Field(nullable=True, default=None)
    """Min length of the answer for Text type"""
    max_length: Mapped[int | None] = Field(nullable=True, default=None)
    """Max length of the answer for Text type"""


class Question_Options(ID, Base):
    """Options available on this question"""

    question_id: Mapped[int] = Field(ForeignKey("Question.id"))
    """Question this option belongs to"""
    value: Mapped[str]
    """Value of this option"""


class Response(Timestamp, ID, Base):
    """Response to a question"""

    user_id: Mapped[UUID]
    """User that responded to this question"""
    question_id: Mapped[int] = Field(ForeignKey("Question.id"))
    """Question being responded to"""
    form_id: Mapped[int] = Field(ForeignKey("Form.id"))
    """Form this response is for"""


class Answer(ID, Base):
    """(Possibly many) Answers associated with a Response to a question"""

    response_id: Mapped[int] = Field(ForeignKey("Response.id"))
    """Response this answer is associated with"""
    value: Mapped[str]
    """Value of the answer"""
