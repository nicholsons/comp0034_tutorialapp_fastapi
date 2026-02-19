from fastapi.exceptions import HTTPException
from sqlmodel import select

from backend.core.deps import SessionDep
from backend.models.models import Games


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
