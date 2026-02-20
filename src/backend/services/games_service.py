from typing import Any, Optional

from fastapi.exceptions import HTTPException
from sqlmodel import select

from backend.core.deps import SessionDep
from backend.models.models import Country, Games, Host


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
    def get_games_by_id(session: SessionDep, game_id: int) -> Games:
        """ Method to retrieve a game by its ID.
        Args:
            session: SQLModel session
            game_id: Games.id

        Returns:
            Games: Paralympic Games object

        Raises:
            HTTPException 404 Not Found
            """
        result: Optional[Games] = session.get(Games, game_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Games with id {game_id} not found")
        return result

    @staticmethod
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
        data = [dict(row) for row in result]
        if not data:
            return []
        return data
