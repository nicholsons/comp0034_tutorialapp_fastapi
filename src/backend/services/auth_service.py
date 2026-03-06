# Copied and adapted from https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/crud.py

from sqlmodel import select

from backend.core.deps import SessionDep
from backend.core.security import get_password_hash, verify_password
from backend.models.models import User
from backend.models.schemas import UserCreate


class AuthService:
    # Dummy hash to use for timing attack prevention when user is not found
    # This is an Argon2 hash of a random password, used to ensure constant-time comparison
    dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

    @staticmethod
    def create_user(session: SessionDep, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create, update={"hashed_password": get_password_hash(user_create.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_user_by_email(*, session: SessionDep, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        session_user = session.exec(statement).first()
        return session_user

    def authenticate(self, *, session: SessionDep, email: str, password: str) -> User | None:
        db_user = self.get_user_by_email(session=session, email=email)
        if not db_user:
            # Prevent timing attacks by running password verification even when user doesn't exist
            # This ensures the response time is similar whether or not the email exists
            verify_password(password, self.dummy_hash)
            return None
        verified = verify_password(password, db_user.hashed_password)
        if not verified:
            return None
        return db_user
