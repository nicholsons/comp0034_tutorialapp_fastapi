from typing import Optional

from fastapi.exceptions import HTTPException
from sqlmodel import select

from backend.core.deps import SessionDep
from backend.models.models import Question, Response


class QuizService:
    """CRUD operations for the Quiz feature

        Methods:
            get_question(db, g_id): Retrieve a question by its ID.
            get_questions(db): Retrieve all questions.
            get_responses_by_question(db, q_id): Retrieve all responses for a question.
            TBC create_question(db, data): Create a new question.
            TBC create_response(db, data): Create a new response.
        """

    @staticmethod
    def get_question(session: SessionDep, q_id: int) -> Question:
        """ Method to retrieve a question by its ID.
        Args:
            session: SQLModel session
            q_id: Question.id

        Returns:
            Question: Question object

        Raises:
            HTTPException 404 Not Found
            """
        result: Optional[Question] = session.get(Question, q_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Question with id {q_id} not found")
        return result

    @staticmethod
    def get_questions(session: SessionDep) -> list[Question]:
        statement = select(Question)
        result = session.exec(statement).all()
        if not result:
            return []
        return list(result)

    @staticmethod
    def get_responses_by_question(session: SessionDep, q_id: int) -> list[Response]:
        statement = select(Response).where(Response.question_id == q_id)
        result = session.exec(statement).all()
        if not result:
            raise HTTPException(status_code=404, detail=f"No responses found for question with id {q_id}")
        return list(result)
