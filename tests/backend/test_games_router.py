from fastapi.testclient import TestClient

from backend.main import create_app


# Activity 2 uses these, they are later replaced by a fixture in activity 3
# app = create_app()

# Create an instance of the FastAPI test client
# client = TestClient(app)


def test_get_games_ok(client):
    # Use the test client to make a requst to the GET /games endpoint (route)
    response = client.get("/games")
    # Use pytest assertion to verify that the response to the request has a status code of 200
    assert response.status_code == 200, "Should return status code 200"


def test_get_games_by_id_ok(client):
    response = client.get("/games/1")
    assert response.status_code == 200, "Should return status code 200"
    assert response.json().get("id") == 1, "The response should include in the JSON {'id': 1}"


# Tests from activity 3 use the test fixture named client in backend/conftest.py
def test_post_games_succeeds(client):
    games_data = {
        "event_type": "summer",
        "year": 2040,
    }
    response = client.post("/games", json=games_data)
    assert response.status_code == 201, "Should return status code 201"
    assert response.json().get(
        "year") == 2040, "The response should include in the JSON {'year': 2040}"


def test_post_games_validation_error_missing_year(client):
    games_data = {
        "event_type": "winter"
    }
    response = client.post("/games", json=games_data)
    assert response.status_code == 422, "Should return status code 422 as the year field is required"


def test_delete_games_succeeds(client):
    response = client.delete("/games/1")
    assert response.status_code == 204, "Should return status code 204 No Content"


def test_delete_not_existing_games_succeeds(client):
    """ The route should return 204 and not 404

    This test fails - so there is an issue with the route that needs to be fixed
    """
    response = client.delete("/games/389734")
    assert response.status_code == 204, "Should return status code 204 No Content and not 404 for consistent responses"
