from typing import Optional
from enum import Enum
from datetime import datetime


class Application_Status(Enum):
    EXPIRED = -1
    NONE = 0
    APPLIED = 1
    NO_RESPONSE = 2
    IN_PROGRESS = 3
    REJECTED = 4
    ACCEPTED = 5


class Remote_Status(Enum):
    NONE = 0
    HYBRID = 1
    FULL = 2


class Contract_Type(Enum):
    PART_TIME = 1
    FULL_TIME = 2
    B2B = 3


class Experience_Level(Enum):
    INTERN = 0
    ENTRY = 1
    JUNIOR = 2
    MID = 3
    SENIOR = 4
    LEAD = 5
    EXECUTIVE = 6


class Recruiter_Type(Enum):
    HR = 0
    LEAD = 1
    CEO = 2


class Posting:
    """Posting details"""

    url: str
    """URL to a posting"""
    position: str
    """Position title"""
    organisation_id: int

    status: Application_Status
    remote: Remote_Status
    experience: Experience_Level
    contract: Contract_Type
    recruiter: Recruiter_Type

    salary_min: Optional[int]
    salary_max: Optional[int]
    required_years: int
    """Required years of experience"""

    country: str
    contact: str
    """Contact with recruiter"""

    requirements: str
    description: str
    tasks: str
    amenities: str
    work_hours: str

    notes: str
    """Personal notes about posting/job"""
    questions: str
    """Questions regarding posting/job"""

    posted: datetime
    updated: datetime


class Posting_Progress:
    """Job application progress"""

    posting_id: int
    initial_response: bool
    initial_call: bool
    general_interview: bool
    tech_assessment: bool
    tech_interview: bool
    final_answer: bool


class Posting_Technology:
    """Used Technologies according to posting"""

    posting_id: int
    technology_id: int
    experience: Optional[int]
    """Required years of experience or proficiency level"""
