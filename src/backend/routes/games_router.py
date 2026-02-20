from fastapi import APIRouter

from backend.core.deps import SessionDep
from backend.models.models import Games, Paralympics
from backend.services.games_service import GamesService

router = APIRouter(
    # prefix="/api/games",
)

crud = GamesService()


@router.get("/games", response_model=list[Games])
def get_games(session: SessionDep):
    """ Returns the data for all Paralympics"""
    games = crud.get_games(session)
    return games


@router.get("/all", response_model=list[Paralympics])
def get_chart_data(session: SessionDep):
    """ Returns data for the charts

    The data is from a query that joins the Games, Host and Country tables. The result
    has the same data attributes as used for creating the charts in the
    Dash/Streamlit/Flask activities in weeks 1 to 5
    """
    data = crud.get_chart_data(session)
    return data


@router.get("/games/{games_id}", response_model=Games)
def get_games_by_id(session: SessionDep, games_id: int):
    """ Returns the data for one Paralympics by its id """
    games = crud.get_games_by_id(session, games_id)
    return games

