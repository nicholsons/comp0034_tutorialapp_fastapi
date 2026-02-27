""" Schemas for the paralympics app

This module contains:
- Base classes defining core fields
- SQLModel database table classes
- Create schemas for POST requests
- Read schemas for GET responses
- Update schemas for PUT/PATCH requests

Key points:
- All Base classes inherit from SQLModel
- Database models inherit from Base and add table=True
- Create schemas inherit from Base (without id)
- Read schemas inherit from Base and include id field
- Read schemas use Pydantic v2 syntax: `model_config = ConfigDict(from_attributes=True)`
- Update schemas have all fields as Optional for partial updates
- Validators are preserved where applicable
"""
from typing import Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class GamesBase(SQLModel):
    """Base schema for Games with core fields"""
    event_type: str
    year: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    countries: Optional[int] = None
    events: Optional[int] = None
    sports: Optional[int] = None
    participants_m: Optional[int] = None
    participants_f: Optional[int] = None
    participants: Optional[int] = None
    highlights: Optional[str] = None
    url: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        allowed = ["winter", "summer"]
        value = value.lower()
        if value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        value = int(value)
        if value < 1960 or value > 9999:
            raise ValueError(f"{value} must be between 1960 and 9999")
        return value


class GamesCreate(GamesBase):
    """Schema for creating a new Games record"""
    pass


class GamesRead(GamesBase):
    """Schema for reading a Games record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class GamesUpdate(SQLModel):
    """Schema for updating a Games record - all fields optional"""
    event_type: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    countries: Optional[int] = None
    events: Optional[int] = None
    sports: Optional[int] = None
    participants_m: Optional[int] = None
    participants_f: Optional[int] = None
    participants: Optional[int] = None
    highlights: Optional[str] = None
    url: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            allowed = ["winter", "summer"]
            value = value.lower()
            if value not in allowed:
                raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: Optional[int]) -> Optional[int]:
        if value is not None:
            value = int(value)
            if value < 1960 or value > 9999:
                raise ValueError(f"{value} must be between 1960 and 9999")
        return value


class TeamBase(SQLModel):
    """Base schema for Team with core fields"""
    code: str
    name: str
    region: Optional[str] = None
    member_type: str
    notes: Optional[str] = None
    country_id: Optional[str] = None

    @field_validator("member_type")
    @classmethod
    def validate_member_type(cls, value: str) -> str:
        allowed = ["country", "team", "dissolved", "construct"]
        if value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: Optional[str]) -> Optional[str]:
        allowed = ["Asia", "Europe", "Africa", "America", "Oceania"]
        if value is not None and value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value


class TeamCreate(TeamBase):
    """Schema for creating a new Team record"""
    pass


class TeamRead(TeamBase):
    """Schema for reading a Team record"""
    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(SQLModel):
    """Schema for updating a Team record - all fields optional"""
    name: Optional[str] = None
    region: Optional[str] = None
    member_type: Optional[str] = None
    notes: Optional[str] = None
    country_id: Optional[str] = None

    @field_validator("member_type")
    @classmethod
    def validate_member_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            allowed = ["country", "team", "dissolved", "construct"]
            if value not in allowed:
                raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: Optional[str]) -> Optional[str]:
        allowed = ["Asia", "Europe", "Africa", "America", "Oceania"]
        if value is not None and value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value


class DisabilityBase(SQLModel):
    """Base schema for Disability with core fields"""
    description: str


class DisabilityCreate(DisabilityBase):
    """Schema for creating a new Disability record"""
    pass


class DisabilityRead(DisabilityBase):
    """Schema for reading a Disability record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class DisabilityUpdate(SQLModel):
    """Schema for updating a Disability record - all fields optional"""
    description: Optional[str] = None


class HostBase(SQLModel):
    """Base schema for Host with core fields"""
    place_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_id: Optional[int] = None


class HostCreate(HostBase):
    """Schema for creating a new Host record"""
    pass


class HostRead(HostBase):
    """Schema for reading a Host record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class HostUpdate(SQLModel):
    """Schema for updating a Host record - all fields optional"""
    place_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_id: Optional[int] = None


class CountryBase(SQLModel):
    """Base schema for Country with core fields"""
    country_name: str


class CountryCreate(CountryBase):
    """Schema for creating a new Country record"""
    pass


class CountryRead(CountryBase):
    """Schema for reading a Country record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class CountryUpdate(SQLModel):
    """Schema for updating a Country record - all fields optional"""
    country_name: Optional[str] = None


class QuestionBase(SQLModel):
    """Base schema for Question with core fields"""
    question_text: str


class QuestionCreate(QuestionBase):
    """Schema for creating a new Question record"""
    pass


class QuestionRead(QuestionBase):
    """Schema for reading a Question record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class QuestionUpdate(SQLModel):
    """Schema for updating a Question record - all fields optional"""
    question_text: Optional[str] = None


class ResponseBase(SQLModel):
    """Base schema for Response with core fields"""
    question_id: Optional[int] = None
    response_text: str
    is_correct: bool


class ResponseCreate(ResponseBase):
    """Schema for creating a new Response record"""
    pass


class ResponseRead(ResponseBase):
    """Schema for reading a Response record"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class ResponseUpdate(SQLModel):
    """Schema for updating a Response record - all fields optional"""
    question_id: Optional[int] = None
    response_text: Optional[str] = None
    is_correct: Optional[bool] = None



class ParalympicsRead(SQLModel):
    """Response model for 'all data' endpoint"""
    country_name: str
    event_type: str
    year: Optional[int] = None
    place_name: Optional[str] = None
    events: Optional[int] = None
    sports: Optional[int] = None
    countries: Optional[int] = None
    participants_m: Optional[int] = None
    participants_f: Optional[int] = None
    participants: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
