from fastapi import APIRouter

from backend.core.deps import SessionDep
from backend.models.models import Games
from backend.services.games_service import GamesService

router = APIRouter(
    prefix="/api/games",
    tags=["games"],
    responses={404: {"description": "Not found"}}
)

crud = GamesService()


@router.get("/", response_model=list[Games])
def get_games(session: SessionDep):
    games = crud.get_all(session)
    return games


@router.get("/{games_id}", response_model=Games)
def get_one_games(session: SessionDep, games_id: int):
    games = crud.get_one(session, games_id)
    return games
