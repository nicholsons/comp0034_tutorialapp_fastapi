from faker import Faker

fake = Faker()


def test_signup_success(client):
    signup_data = {
        "email": fake.email(),
        "password": fake.password(),
    }
    response = client.post(
        "/signup", json=signup_data
    )
    data = response.json()

    # Signup route returns 201 Created on success and returns the user object
    assert response.status_code == 201, "Signup route should return 201 status code"
    assert data["id"] is not None, "A created user should have an id."


def test_signup_data_incomplete(client):
    # No password
    signup_data = {
        "email": fake.email(),
    }
    response = client.post(
        "/signup", json=signup_data
    )
    # This should raise 422 as it fails the Pydantic schema validation
    assert response.status_code == 422, "Should raise status code 422, does not match UserCreate schema"


def test_signup_invalid_password(client):
    # Password minimum 4 characters
    signup_data = {
        "email": fake.email(),
        "password": "foo",
    }
    response = client.post(
        "/signup", json=signup_data
    )
    assert response.status_code == 422
    assert "should have at least 4 characters" in response.json()["detail"][0]["msg"]

