from typing import Any, Optional

from fastapi.exceptions import HTTPException
from sqlmodel import select

from backend.core.deps import SessionDep
from backend.models.models import Question, Response
from backend.models.schemas import QuestionCreate, ResponseCreate


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
    def get_response(session: SessionDep, r_id: int) -> Response:
        """ Method to retrieve a repsonse by its ID.
        Args:
            session: SQLModel session
            r_id: Response.id

        Returns:
            Response: Response object

        Raises:
            HTTPException 404 Not Found
            """
        result: Optional[Question] = session.get(Response, r_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Response with id {r_id} not found")
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
            raise HTTPException(status_code=404,
                                detail=f"No responses found for question with id {q_id}")
        return list(result)

    @staticmethod
    def create_question(db: SessionDep, question_create: QuestionCreate) -> Question:
        """ Method to create a new Question.

        Args:
            db: SQLModel session
            question_create: data for a new Question object

        Returns:
            Question: Question object
            """
        new_q = Question.model_validate(question_create)
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        return new_q

    @staticmethod
    def create_response(db: SessionDep, response_create: ResponseCreate) -> Response:
        """ Method to create a new response.

        Args:
            db: SQLModel session
            response_create: data for a new Response object

        Returns:
            Response: Response object
        """
        new_r = Response.model_validate(response_create)
        db.add(new_r)
        db.commit()
        db.refresh(new_r)
        return new_r

    def delete_question(self, session: SessionDep, q_id: int) -> Any:
        """ Delete a Question by its ID.

        Args:
            session: FastAPI dependency with SQLModel session
            q_id: id of the Question to delete

        Returns:
            {} if the Question is deleted, or None if not found
            """
        q = self.get_question(session, q_id)
        if not q:
            return None
        else:
            session.delete(q)
            session.commit()
            return {}

    def delete_response(self, session: SessionDep, response_id: int) -> Any:
        """ Delete a Response by its ID.

        Args:
            session: FastAPI dependency with SQLModel session
            response_id: id of the Response to delete

        Returns:
            {} if the response is deleted, or None if not found
            """
        r = self.get_response(session, response_id)
        if not r:
            return None
        else:
            session.delete(r)
            session.commit()
            return {}

    def update_question(self, session: SessionDep, q_id: int, update_data: dict):
        """ Method to update a Question object.

        This method can be used by either PUT or PATCH. The route code will handle the
        validation against the schema.

        Args:
            session: FastAPI dependency with SQLModel session
            q_id: id of the Question to update
            update_data: data to update the Question object

        Returns:
            q: Question object
            """
        q = self.get_question(session, q_id)
        if q is None:
            return None

        for key, value in update_data.items():
            setattr(q, key, value)

        session.commit()
        session.refresh(q)
        return q

    def update_response(self, session: SessionDep, r_id: int, update_data: dict):
        """ Method to update a Response object.

        This method can be used by either PUT or PATCH. The route code will handle the
        validation against the schema.

        Args:
            session: FastAPI dependency with SQLModel session
            r_id: id of the Response to update
            update_data: data to update the Response object

        Returns:
            r: Response object
            """
        r = self.get_response(session, r_id)
        if r is None:
            return None

        for key, value in update_data.items():
            setattr(r, key, value)

        session.commit()
        session.refresh(r)
        return r
