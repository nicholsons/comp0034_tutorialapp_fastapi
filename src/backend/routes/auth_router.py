# Adapted from
# https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/api/routes/login.py
# https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/api/routes/users.py

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.core import security
from backend.core.deps import CurrentUser, SessionDep
from backend.models.schemas import Token, UserCreate, \
    UserRead
from backend.services.auth_service import AuthService

router = APIRouter(tags=["login"])
crud = AuthService()


@router.post("/login/access-token")
def login_access_token(
        session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Use email as the username and the password to log them in and return the user
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    # If the user is found, then generate a token
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return Token(
        access_token=security.create_access_token(user.id)
    )


@router.post("/login/test-token", response_model=UserRead)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/signup", response_model=UserRead)
def register_user(session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    try:
        user_create = UserCreate.model_validate(user_in)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid email or password {str(e)}")
    user = crud.create_user(session=session, user_create=user_create)
    return user
