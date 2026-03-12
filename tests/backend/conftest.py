import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, StaticPool, create_engine, select

from backend.core.config import get_settings
from backend.core.db import add_data
from backend.core.deps import get_current_user, get_db
from backend.main import create_app
from backend.models.models import User, Games


@pytest.fixture(name="session")
def session_fixture(set_test_env):
    """ Creates a test database dependency.

    Rolls back all transactions after each test.

    From https://github.com/fastapi/sqlmodel/discussions/940

    Note: the test_paralympics.db contains data, if you create an in memory database you will also
    need to seed some sample data for testing.
    """
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
        # echo=True Added so you can see what is happening when you run tests that use the database
        # you may prefer to set this to False
    )
    SQLModel.metadata.create_all(bind=engine)
    # Add data if empty
    with Session(engine) as session:
        games = session.exec(select(Games)).first()
        if not games:
            add_data(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    nested = connection.begin_nested()

    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """ Creates a test client that overrides the database dependency.
     https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#client-fixture
     """

    def get_session_override():
        return session

    app = create_app()
    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Creates a test user in the database"""
    from backend.core.security import get_password_hash

    test_user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    return test_user


@pytest.fixture(name="client_with_auth")
def client_with_auth_fixture(session: Session, test_user: User):
    """Creates a test client with CurrentUser dependency overridden with a test user"""

    def get_session_override():
        return session

    def get_current_user_override():
        return test_user

    app = create_app()
    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# The following commented out version of the session fixture is from the FastAPI documentation
# left in so you can use this instead if you prefer


# @pytest.fixture(name="session")
# def session_fixture():
#     """ Creates a test database session.
#     https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#pytest-fixtures
#
#     """
#     engine = create_engine(
#         settings.test_database_url,
#         connect_args={"check_same_thread": False},
#         poolclass=StaticPool
#     )
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session
#
#     # Dispose of the engine to close all connections
#     engine.dispose()
