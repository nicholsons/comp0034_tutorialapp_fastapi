from typing import Any, Optional

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from backend.core.deps import SessionDep
from backend.models.models import Country, Games, Host
from backend.models.schemas import GamesCreate


class GamesService:
    """CRUD operations for the Games model.

        Provides methods to create, retrieve, update, and delete Games
        in the database

        Methods:
            create(db, data): Create a new games.
            get_one(db, g_id): Retrieve a games by its ID.
            get_all(db): Retrieve all games.
            update(db, g_id, data): Update an existing games.
            delete(db, g_id): Delete a games by its ID.
            get_chart_data(db): Retrieves all data attributes from the paralympics database needed
            for thecharts in the front end app.
        """

    @staticmethod
    def get_games_by_id(session: SessionDep, games_id: int) -> Games:
        """ Method to retrieve a game by its ID.
        Args:
            session: SQLModel session
            games_id: Games.id

        Returns:
            Games: Paralympic Games object

        Raises:
            HTTPException 404 Not Found
            """
        result: Optional[Games] = session.get(Games, games_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Games with id {games_id} not found")
        return result

    def get_games(session: SessionDep) -> list[Games]:
        statement = select(Games)
        result = session.exec(statement).all()
        if not result:
            return []
        return list(result)

    @staticmethod
    def get_chart_data(session: SessionDep) -> list[dict[str, Any]]:
        """ Method to return all data from the paralympics database for the charts.

        This does not map to a single table. Needs to be preserved for the front end app.

        Returns:
            data: json format data
        """

        statement = select(
            Country.country_name,
            Games.event_type,
            Games.year,
            Games.start_date,
            Games.end_date,
            Host.place_name,
            Games.events,
            Games.sports,
            Games.countries,
            Games.participants_m,
            Games.participants_f,
            Games.participants,
            Host.latitude,
            Host.longitude,
        ).select_from(Games).join(Games.hosts).join(Country, Host.country_id == Country.id)

        result = session.exec(statement).all()

        # Map tuple results to dictionaries with column names
        column_names = [
            'country_name',
            'event_type',
            'year',
            'start_date',
            'end_date',
            'place_name',
            'events',
            'sports',
            'countries',
            'participants_m',
            'participants_f',
            'participants',
            'latitude',
            'longitude'
        ]

        data = [dict(zip(column_names, row)) for row in result]
        if not data:
            return []
        return data

    @staticmethod
    def create_games(session: SessionDep, games_create: GamesCreate) -> Games:
        """ Method to create a new games.


        Args:
            session: FastAPI dependency with SQLModel session
            games_create: data for a new Paralympic Games object

        Returns:
            Games: Paralympic Games object
            """
        try:
            new_games = Games.model_validate(games_create)
            session.add(new_games)
            session.commit()
            session.refresh(new_games)
            return new_games
        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(status_code=500, detail="Server error. Games not created.")

    def delete_games(self, session: SessionDep, games_id: int) -> Any:
        """ Delete a new paralympic Games

        Args:
            session: FastAPI dependency with SQLModel session
            games_id: id of the Games to delete

        Returns:
            {} if the Games is deleted, or None if not found
            """
        games = self.get_games_by_id(session, games_id)
        if not games:
            return None
        else:
            session.delete(games)
            session.commit()
            return {}

    def update_games(self, session: SessionDep, games_id: int, update_data: dict):
        """ Method to update a Games object.

        This method can be used by either PUT or PATCH. The route code will handle the
        validation against the schema.

        Args:
            session: FastAPI dependency with SQLModel session
            games_id: id of the Games to update
            update_data: data to update the Games object

        Returns:
            games: Paralympic Games object
            """
        games = self.get_games_by_id(session, games_id)
        if games is None:
            return None

        for key, value in update_data.items():
            setattr(games, key, value)

        session.commit()
        session.refresh(games)
        return games
