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


class Form(Meta, Base, schema="forms"):
    """Form metadata"""

    questions: list["Question"] = Relationship(secondary="Form_Questions", default_factory=list)
    """Questions this form has"""


class Form_Questions(Base, schema="forms"):
    """Association of questions to a specific form"""

    form_id: Mapped[int] = Field(ForeignKey("Form.id"), primary_key=True)
    """Form this question is associated with"""
    question_id: Mapped[int] = Field(ForeignKey("Question.id"), primary_key=True)
    """Associated Question"""
    order: Mapped[int] = Field(default=False)
    """Order in which to display this question in a form"""
    required: Mapped[bool] = Field(default=False)
    """Whether this question is mandatory in this form"""


class Question(Meta, Base, schema="forms"):
    """Question data"""

    type: Mapped[str] = Field(default=None, nullable=False)
    """Type of this question. For example Text, Select or Choice"""
    min: Mapped[int | None] = Field(nullable=True, default=None)
    """Min value or length of the answer"""
    max: Mapped[int | None] = Field(nullable=True, default=None)
    """Max value or length of the answer"""
    default: Mapped[str | None] = Field(nullable=True, default=None)
    """Value used as a default value or a placeholder"""

    answers: list["Answer"] = Relationship(default_factory=list)
    """Answers provided to this question"""


class Question_Options(ID, Base, schema="forms"):
    """Options available on this question"""

    question_id: Mapped[int] = Field(ForeignKey("Question.id"))
    """Question this option belongs to"""
    value: Mapped[str]
    """Value of this option"""


class Response(Timestamp, ID, Base, schema="forms"):
    """Response to a question"""

    user_id: Mapped[UUID]
    """User that responded to this question"""
    question_id: Mapped[int] = Field(ForeignKey("Question.id"))
    """Question being responded to"""
    form_id: Mapped[int] = Field(ForeignKey("Form.id"))
    """Form this response is for"""


class Answer(ID, Base, schema="forms"):
    """(Possibly many) Answers associated with a Response to a question"""

    response_id: Mapped[int] = Field(ForeignKey("Response.id"))
    """Response this answer is associated with"""
    value: Mapped[str]
    """Value of the answer"""
