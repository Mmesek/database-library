from .mixins import *

#class Technology_Project(Base):
#    importance: float
#    technology_id: int = Field(foreign_key="technology.id", primary_key=True)
#    project_id: int = Field(foreign_key="project.id", primary_key=True)
    
#    technology: Technology = Relationship()
#    project: Project = Relationship()

class Metadata(Enum):
    Name = 'string'
    Birth = 'date'


class Meta(Name):
    number: Optional[int]
    string: Optional[str]
    date: Optional[datetime]


class User(Name):
    surname: str
    birthday: datetime
    country: str
    city: str
    street: str
    postal: str

class Organisation(Category, URL, Name, table=True):
    # 0 | Legit Inc | www | Scheming
    #experiences: list['Experience'] = Relationship(back_populates="company")
    pass


class HasTechnology(SQLModel):
    importance: float = Field(ge=0, le=100)
    technology_id: int = Field(foreign_key="technology.id", primary_key=True)


class Project_Technologies(SQLModel, table=True):
    importance: float = Field(ge=0, le=100)
    technology_id: int = Field(foreign_key="technology.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    #project: "Project" = Relationship(back_populates="technologies")
    #technology: Technology = Relationship(back_populates="projects")


class Certificate_Technologies(SQLModel, table=True):
    importance: float = Field(ge=0, le=100)
    technology_id: int = Field(foreign_key="technology.id", primary_key=True)
    certificate_id: int = Field(foreign_key="certificate.id", primary_key=True)
    #certificate: "Certificate" = Relationship(back_populates="technologies")
    #technology: Technology = Relationship(back_populates="certificates")


class Technology(Timeframe, Category, Name, table=True):
    # 0 | Python | Programming | 2018 | None | None | 80
    confidency: Optional[int] = Field(ge=0, le=100)
    base: Optional[int] = Field(default=None)
    #certificates: list["Certificate"] = Relationship(back_populates="technologies", link_model=Certificate_Technologies)
    #projects: list["Project"] = Relationship(back_populates="technologies", link_model=Project_Technologies)


class Project(Timeframe, Category, URL, Name, table=True):
    # 0 | Discord Bot | www | RESTful Service | 2019 | None | None | Some description | [Python]
    description: str
    technologies: list[Technology] = Relationship(back_populates="projects",link_model=Project_Technologies)


class Certificate(Price, Timeframe, Category, URL, Name, table=True):
    # 0 | FreeCodeCamp | www | Programming | None | 2022 | None | None | None | None
    expire_at: datetime
    technologies: list[Technology] = Relationship(back_populates="certificates", link_model=Certificate_Technologies)


class Contact(Name, SQLModel, table=True):
    # 0 | email | address@domain.tld
    value: str


class Link(URL, Name, SQLModel, table=True):
    # 0 | Github | www
    pass

class Experience_Projects:
    experience_id: int = Field(foreign_key="experience.id", primary_key=True)
    experience: "Experience" = Relationship(back_populates="projects")
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    project: "Project" = Relationship(back_populates="experiences")

class Experience(Price, Category, Timeframe, ID, SQLModel, table=True):
    # 0 | 2019 | None | None | Web Development | 50 | EUR | Commision | Bot | [Python, SQL] | | 0 (Legit Inc)
    type: str
    title: Optional[str]
    #technologies: Optional[list[Technology]] = Relationship()
    projects: list[Project] = Relationship(back_populates="experiences")
    company_id: int = Field(default=None, foreign_key="organisation.id")
    company: Organisation = Relationship(back_populates="experiences")

    @property
    def technologies(self):
        return [{link.technology.name: link.importance for link in project.technology_links} for project in self.projects]
        # TODO: Flat list of technology names from most used to least
        # TODO: Normalize importance data and apply project duration as a modifier. Longer project with higher importance should contribute much more to score than short one
        # NOTE: Currently it's a list of mapping name to importance
