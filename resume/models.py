from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from ..utils.mixins import Name, Category, Timeframe, Price, URL


class Organisation(Category, URL, Name, table=True):
    experiences: list["Experience"] = Relationship(back_populates="company")


class Project_Technologies(SQLModel, table=True):
    importance: float = Field(ge=0, le=100)
    """Importance of this Technology in Project"""
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    technology_id: int = Field(foreign_key="technology.id", primary_key=True)


class Certificate_Technologies(SQLModel, table=True):
    importance: float = Field(ge=0, le=100)
    """Importance of this Technology in Certificate"""
    hours: Optional[float]
    """Hours of Certificate for this Technology"""

    certificate_id: int = Field(foreign_key="certificate.id", primary_key=True)
    technology_id: int = Field(foreign_key="technology.id", primary_key=True)


class Experience_Projects(SQLModel, table=True):
    experience_id: int = Field(foreign_key="experience.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

    experience: "Experience" = Relationship(back_populates="projects")
    project: "Project" = Relationship(back_populates="experiences")


class Technology(Timeframe, Category, Name, table=True):
    confidency: Optional[int] = Field(ge=0, le=100)
    """Confency in this Technology"""
    base: Optional[int] = Field(default=None, foreign_key="technology.id")
    """Base technology this technology extends"""

    certificates: list["Certificate"] = Relationship(back_populates="technologies", link_model=Certificate_Technologies)
    projects: list["Project"] = Relationship(back_populates="technologies", link_model=Project_Technologies)


class Project(Timeframe, Category, URL, Name, table=True):
    description: str
    """Description of this Project"""
    hours: Optional[float]
    """Hours spent on this Project"""

    technologies: list[Technology] = Relationship(back_populates="projects", link_model=Project_Technologies)
    """Technologies used by this Project"""


class Certificate(Price, Timeframe, Category, URL, Name, table=True):
    hours: Optional[float]
    """Hours this Certificate took to complete"""
    expire_at: Optional[datetime]
    """Date when this certificate expires, if at all"""
    id: Optional[str]
    """Certificate's ID"""

    technologies: list[Technology] = Relationship(back_populates="projects", link_model=Project_Technologies)
    """Technologies required by this Certificate"""


class Experience(Price, Category, Timeframe, Name, table=True):
    type: str
    hours: Optional[float]
    company_id: int = Field(default=None, foreign_key="organisation.id")

    projects: list[Project] = Relationship(back_populates="experiences", link_model=Experience_Projects)

    @property
    def technologies(self):
        return [
            {technology.name: technology.importance for technology in project.technologies} for project in self.projects
        ]
        # TODO: Flat list of technology names from most used to least
        # TODO: Normalize importance data and apply project duration as a modifier. Longer project with higher importance should contribute much more to score than short one
        # NOTE: Currently it's a list of mapping name to importance
