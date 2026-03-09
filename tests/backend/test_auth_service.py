""" Example of a test that does not use the test client but does use the session fixture. """
from faker import Faker
from sqlmodel import Session

from backend.models.schemas import UserCreate
from backend.services.auth_service import AuthService

fake = Faker()

# This test does not use the test client but does use the session fixture
def test_create_user(session: Session) -> None:
    email = fake.email()
    password = fake.password()
    user_in = UserCreate(email=email, password=password)
    crud = AuthService()
    user = crud.create_user(session=session, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password"), "User model must include hashed_password attribute"
    assert user.hashed_password is not password, "The hashed_password attribute must not be equal to password"
