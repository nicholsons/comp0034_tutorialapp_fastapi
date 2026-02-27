from typing import Any

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from backend.core.deps import SessionDep
from backend.models.schemas import GamesCreate, GamesRead, GamesUpdate, ParalympicsRead
from backend.services.games_service import GamesService

router = APIRouter(
    # prefix="/api/games",  # Not used in order to match the route defined in the front end app
)

crud = GamesService()


@router.get("/games", response_model=list[GamesRead])
def get_games(session: SessionDep) -> Any:
    """ Returns the data for all Paralympics"""
    games = crud.get_games(session)
    return games


@router.get("/all", response_model=list[ParalympicsRead])
def get_chart_data(session: SessionDep) -> Any:
    """ Returns data for the charts

    The data is from a query that joins the Games, Host and Country tables. The result
    has the same data attributes as used for creating the charts in the
    Dash/Streamlit/Flask activities in weeks 1 to 5
    """
    data = crud.get_chart_data(session)
    return data


@router.get("/games/{games_id}", response_model=GamesRead)
def get_games_by_id(session: SessionDep, games_id: int) -> Any:
    """ Returns the data for one Paralympics by its id """
    games = crud.get_games_by_id(session, games_id)
    return games


@router.post("/games", response_model=GamesRead, status_code=status.HTTP_201_CREATED)
def create_games(session: SessionDep, games_data: GamesCreate) -> Any:
    """ Creates a new paralympic Games """
    new_games = crud.create_games(session, games_data)
    return new_games


@router.delete("/games/{games_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_games(session: SessionDep, games_id: int) -> Any:
    """ Delete a new paralympic Games

    The version returns 404 if the Games was not found and 204 if it was deleted
    You could modify and return 204 in both cases

    Returns:
        {}: empty dict
    """
    games = crud.delete_games(session, games_id)
    if games is None:
        raise HTTPException(status_code=404, detail=f"Games with id {games_id} not found")
    else:
        return {}


@router.put("/games/{games_id}")
def update_games_put(games_id: int, data: GamesCreate, session: SessionDep):
    """ Updates a paralympic Games by replacing the entire resource

    Note: model_dump() expects all fields to be present in the data and applies the validation
    """
    games = crud.update_games(session=session, games_id=games_id, update_data=data.model_dump())
    return games


@router.patch("/games/{games_id}")
def update_games_patch(games_id: int, data: GamesUpdate, session: SessionDep):
    """ Partial updates for a paralympic Games

    Note: data.model_dump(exclude_unset=True) allows for only some fields to be present in the data
    """
    games = crud.update_games(session=session, games_id=games_id,
                              update_data=data.model_dump(exclude_unset=True))
    return games
