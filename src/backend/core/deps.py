from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from backend.core.config import get_settings
from backend.core.db import get_engine
from backend.models.models import User
from backend.models.schemas import TokenPayload


def get_db():
    """Dependency for database session

    Yields:
        session: SQLModel session

    Note: you don't need to session.close() as the context manager handles this
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# -----------------
# Auth dependencies
# -----------------

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get the current authenticated user from JWT token.

    Args:
        session: Database session dependency
        token: Dependency, JWT token from OAuth2 authentication

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is invalid (403) or user not found (404)
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
