from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from backend.core.db import engine


def get_db():
    """ Dependency for database session

    Yields:
        session: SQLModel session

    Note: you don't need to session.close() as the context manager handles this
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
