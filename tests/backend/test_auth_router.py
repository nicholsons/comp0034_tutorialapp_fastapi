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


def test_login_access_token_succeeds(client, test_user):
    password = "testpassword"
    response = client.post(
        "/login/access-token",
        data={"username": test_user.email, "password": password},
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["access_token"] != ""
    assert data["token_type"] == "bearer"


def test_login_access_token_fails_incorrect_password(client, test_user):
    password = "wrong"
    response = client.post(
        "/login/access-token",
        data={"username": test_user.email, "password": password},
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_access_token_fails_user_not_in_db(client):
    response = client.post(
        "/login/access-token",
        data={"username": fake.email, "password": fake.password},
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Incorrect email or password'}
