from typing import Any

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
        """

    @staticmethod
    def get_one(session: SessionDep, id: int) -> Games:
        result = session.get(Games, id)
        if not result:
            raise HTTPException(status_code=404, detail="Games not found")
        return result

    @staticmethod
    def get_all(session: SessionDep) -> list[Games]:
        statement = select(Games)
        result = session.exec(statement).all()
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

        rows = session.exec(statement).all()
        return rows
        # Convert rows to dicts for consistent JSON keys
        # return [dict(row._mapping) for row in rows]
