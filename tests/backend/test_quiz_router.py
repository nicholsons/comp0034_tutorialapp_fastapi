""" Examples of tests that use the FastAPI test client.

The client fixture is defined in tests/backend/conftest.py
"""


def test_get_questions_ok(client):
    response = client.get("/questions")
    assert response.status_code == 200, "Should return status code 200"


def test_get_question(client):
    response = client.get("/questions/1")
    assert response.status_code == 200
    assert response.json().get(
        'question_text'), "json response must contain the 'question_text' field e.g. {'question_text': 'Some text'}"
    assert response.json().get('id') == 1, "json response must contain 'id': 1"


def test_get_question_not_found(client):
    response = client.get(f"/questions/12345679")
    assert response.status_code == 404
    assert response.json()["detail"] == "Question with id 12345679 not found"


def test_create_question_unauthorised(client):
    response = client.post("/questions", json={"question_text": "Some text"})
    assert response.status_code == 401, "Create question should return status code 401 as the user is not authenticated."


def test_create_question_authorised(client_with_auth):
    response = client_with_auth.post("/questions", json={"question_text": "Some text"})
    assert response.status_code == 201, "Create question should return status code 201 as the user is authenticated."
