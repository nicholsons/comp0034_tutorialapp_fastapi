from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from backend.core.deps import SessionDep
from backend.models.schemas import QuestionCreate, QuestionRead, QuestionUpdate, ResponseCreate, \
    ResponseRead, ResponseUpdate
from backend.services.quiz_service import QuizService

router = APIRouter()

crud = QuizService()


@router.get("/questions", response_model=list[QuestionRead])
def get_questions(session: SessionDep):
    """ Returns the data for all questions

    NB: Front-end route needs to be changed from '/question' to '/questions'
    """
    questions = crud.get_questions(session)
    return questions


@router.get("/questions/{q_id}", response_model=QuestionRead)
def get_question(session: SessionDep, q_id: int):
    """ Returns the data for one questions

    NB: Front-end route needs to be changed from '/question/q_id' to '/questions/{q_id}'
    """
    question = crud.get_question(session, q_id=q_id)
    return question


@router.get("/questions/{q_id}/responses", response_model=list[ResponseRead])
def get_responses_for_question(session: SessionDep, q_id: int):
    """ Returns the data for all responses for a given question

    NB: Front-end route needs to be changed from '/question/search' to '/questions/{q_id}/responses'
    """
    responses = crud.get_responses_by_question(session, q_id)
    return responses


@router.post("/questions", response_model=QuestionRead)
def create_question(session: SessionDep, question_data: QuestionCreate):
    """ Creates a new question  """
    new_question = crud.create_games(session, question_data)
    return new_question


@router.post("/responses", response_model=ResponseRead)
def create_question(session: SessionDep, question_data: QuestionCreate):
    """ Creates a new question  """
    new_question = crud.create_games(session, question_data)
    return new_question


@router.delete("/responses/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(session: SessionDep, response_id: int):
    """ Delete a Response

    The version returns 404 if the Response was not found and 204 if it was deleted
    You could modify and return 204 in both cases

    Returns:
        {}: empty dict
    """
    resp = crud.delete_response(session, response_id)
    if resp is None:
        raise HTTPException(status_code=404, detail=f"Response with id {response_id} not found")
    else:
        return {}


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(session: SessionDep, question_id: int):
    """ Delete a Question

    The version returns 404 if the Question was not found and 204 if it was deleted
    You could modify and return 204 in both cases

    Returns:
        {}: empty dict
    """
    resp = crud.delete_question(session, question_id)
    if resp is None:
        raise HTTPException(status_code=404, detail=f"Response with id {question_id} not found")
    else:
        return {}


@router.put("/questions/{question_id}")
def replace_question(question_id: int, data: QuestionCreate, session: SessionDep):
    """ Updates a Question by replacing the entire resource

    Note: model_dump() expects all fields to be present in the data and applies the validation
    """
    q = crud.update_question(session=session, q_id=question_id, update_data=data.model_dump())
    return q


@router.patch("/questions/{question_id}")
def update_question(question_id: int, data: QuestionUpdate, session: SessionDep):
    """ Partial updates for a Question

    Note: data.model_dump(exclude_unset=True) allows for only some fields to be present in the data
    """
    q = crud.update_question(session=session, q_id=question_id,
                             update_data=data.model_dump(exclude_unset=True))
    return q


@router.put("/responses/{response_id}")
def update_response(response_id: int, data: ResponseCreate, session: SessionDep):
    """ Updates a Response by replacing the entire resource

    Note: model_dump() expects all fields to be present in the data and applies the validation
    """
    r = crud.update_response(session=session, games_id=response_id, update_data=data.model_dump())
    return r


@router.patch("/responses/{response_id}")
def replace_response(response_id: int, data: ResponseUpdate, session: SessionDep):
    """ Partial updates for a Response

    Note: data.model_dump(exclude_unset=True) allows for only some fields to be present in the data
    """
    r = crud.update_response(session=session, response_id=response_id,
                             update_data=data.model_dump(exclude_unset=True))
    return r
