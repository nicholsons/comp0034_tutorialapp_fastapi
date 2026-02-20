""" Model classes for the paralympics database

From COMP0035

"""
from typing import Optional

from pydantic import field_validator
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel


class GamesHost(SQLModel, table=True):
    __tablename__ = "games_host"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    host_id: int = Field(default=None, foreign_key="host.id")


class GamesDisability(SQLModel, table=True):
    __tablename__ = "games_disability"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    disability_id: int = Field(default=None, foreign_key="disability.id")


class GamesTeam(SQLModel, table=True):
    __tablename__ = "games_team"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    team_id: str = Field(default=None, foreign_key="team.code")


class Games(SQLModel, table=True):
    __tablename__ = "games"
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str
    year: int
    start_date: Optional[str]
    end_date: Optional[str]
    countries: Optional[int]
    events: Optional[int]
    sports: Optional[int]
    participants_m: Optional[int]
    participants_f: Optional[int]
    participants: Optional[int]
    highlights: Optional[str]
    url: Optional[str]
    hosts: list["Host"] = Relationship(back_populates="games", link_model=GamesHost)
    disabilities: list["Disability"] = Relationship(back_populates="games",
                                                    link_model=GamesDisability)
    teams: list["Team"] = Relationship(back_populates="games", link_model=GamesTeam)

    __table_args__ = (
        CheckConstraint("event_type IN ('winter', 'summer')"),
        CheckConstraint("year BETWEEN 1960 AND 9999")
    )

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


class Team(SQLModel, table=True):
    __tablename__ = "team"
    code: str = Field(primary_key=True)  # Not set by the database
    name: str
    region: Optional[str]
    member_type: str
    notes: Optional[str]
    country_id: Optional[str] = Field(default=None, foreign_key="country.id")

    games: list["Games"] = Relationship(back_populates="teams", link_model=GamesTeam)

    __table_args__ = (
        CheckConstraint("member_type IN ('country', 'team', 'dissolved', 'construct')"),
        CheckConstraint("region IN ('Asia', 'Europe', 'Africa', 'America', 'Oceania')")
    )

    @field_validator("member_type", mode="after")
    @classmethod
    def validate_member_type(cls, value: str) -> str:
        allowed = ["country", "team", "dissolved", "construct"]
        if value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("region", mode="after")
    @classmethod
    def validate_region(cls, value: Optional[str]) -> Optional[str]:
        allowed = ["Asia", "Europe", "Africa", "America", "Oceania"]
        if value is not None and value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value


class Disability(SQLModel, table=True):
    __tablename__ = "disability"
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str

    games: list["Games"] = Relationship(back_populates="disabilities", link_model=GamesDisability)


class Host(SQLModel, table=True):
    __tablename__ = "host"
    id: Optional[int] = Field(default=None, primary_key=True)
    place_name: str = Field(unique=True)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    country_id: Optional[int] = Field(default=None, foreign_key="country.id")

    games: list["Games"] = Relationship(back_populates="hosts", link_model=GamesHost)


class Country(SQLModel, table=True):
    __tablename__ = "country"
    id: Optional[int] = Field(default=None, primary_key=True)
    country_name: str


class Question(SQLModel, table=True):
    __tablename__ = "question"
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    responses: list["Response"] = Relationship(back_populates="question")


class Response(SQLModel, table=True):
    __tablename__ = "response"
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="question.id")
    response_text: str
    is_correct: bool
    question: "Question" = Relationship(back_populates="responses")


# Response model for the 'all data'
class Paralympics(SQLModel):
    country_name: str
    event_type: str
    year: int | None = None
    place_name: str | None = None
    events: int | None = None
    sports: str | None = None
    countries: int | None = None
    participants_m: int | None = None
    participants_f: int | None = None
    countries: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    end_date: str | None = None
    place_name: str | None = None
    events: int | None = None
    sports: int | None = None
    countries: int | None = None
    participants_m: int | None = None
    participants_f: int | None = None
    participants: int | None = None
    latitude: float | None = None
    longitude: float | None = None
