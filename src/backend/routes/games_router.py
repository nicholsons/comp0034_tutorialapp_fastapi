from fastapi import APIRouter

from backend.core.deps import SessionDep
from backend.models.models import Games, Paralympics
from backend.services.games_service import GamesService

router = APIRouter(
    prefix="/api/games",
    tags=["games"],
    responses={404: {"description": "Not found"}}
)

crud = GamesService()


@router.get("/", response_model=list[Games])
def get_games(session: SessionDep):
    """ Returns the data for all Paralympics"""
    games = crud.get_all(session)
    return games


@router.get("/chartdata/", response_model=list[Paralympics])
def get_chart_data(session: SessionDep):
    """ Returns data for the charts

    Does not map to a single table, maps to a join query result that
    has the same data fields as used for creating the charts in the
    Dash/Streamlit/Flask activities in weeks 1 to 5
    """
    data = crud.get_chart_data(session)
    print(data)
    return data


@router.get("/{games_id}", response_model=Games)
def get_one_games(session: SessionDep, games_id: int):
    """ Returns the data for one Paralympics by its id """
    games = crud.get_one(session, games_id)
    return games

