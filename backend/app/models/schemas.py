from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    SHORTLISTED = "Shortlisted"
    INTERVIEW = "Interview"
    SELECTED = "Selected"
    REJECTED = "Rejected"


class ApplicationBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=120)
    role: str = Field(..., min_length=1, max_length=120)
    package: Optional[str] = Field(default=None, max_length=50)
    application_date: date
    status: ApplicationStatus = ApplicationStatus.APPLIED
    notes: Optional[str] = Field(default=None, max_length=1000)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: Optional[str] = Field(default=None, min_length=1, max_length=120)
    role: Optional[str] = Field(default=None, min_length=1, max_length=120)
    package: Optional[str] = Field(default=None, max_length=50)
    application_date: Optional[date] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class Application(ApplicationBase):
    id: str
    created_at: str
    updated_at: str


class ApplicationStats(BaseModel):
    total: int
    applied: int
    shortlisted: int
    interview: int
    selected: int
    rejected: int


class ResumeAnalysis(BaseModel):
    detected_skills: list[str]
    missing_skills: list[str]
    relevant_technologies: list[str]
    strengths: list[str]
    improvement_areas: list[str]
    suggestions: list[str]
    summary: str


class JobMatchRequest(BaseModel):
    job_description: str = Field(..., min_length=20)


class JobMatchResult(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]
    relevant_technologies: list[str]
    alignment_percentage: int
    suggestions: list[str]


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    uploaded_at: str


class AssistantQuery(BaseModel):
    question: str = Field(..., min_length=3)


class SourceChunk(BaseModel):
    document: str
    snippet: str


class AssistantResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
