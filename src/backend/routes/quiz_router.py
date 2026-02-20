

from fastapi import APIRouter

from backend.core.deps import SessionDep
from backend.models.models import Question, Response
from backend.services.quiz_service import QuizService

router = APIRouter()

crud = QuizService()

@router.get("/question", response_model=list[Question])
def get_questions(session: SessionDep):
    """ Returns the data for all questions"""
    questions = crud.get_questions(session)
    return questions


@router.get("/question/{q_id}", response_model=Question)
def get_question(session: SessionDep, q_id: int):
    """ Returns the data for one questions"""
    question = crud.get_question(session, q_id=q_id)
    return question


@router.get("/response/search", response_model=list[Response])
def get_responses_for_question(session: SessionDep, question_id: int):
    """ Returns the data for all responses for a given question"""
    responses = crud.get_responses_by_question(session, question_id)
    return responses
