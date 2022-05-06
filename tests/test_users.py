import pytest

from jose import jwt  # For token.

from app import schemas
from app.config import settings


# Pass in the body as json. The expected fields from the relevant schema of the body must be passed in.
# In this case, it's "UserCreate" schema.
def test_create_user(client):  # client object is referenced from fixture.
    res = client.post(
        "/users/", json={"email": "1@1.com", "password": "1"})
    # Using the model itself, pytest can validate if ALL the unpacked fields and properties are in fact included, before sending.
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "1@1.com"  # Testing for email field.
    assert res.status_code == 201  # Created.


# Must be sent as formdata, and not as json. Creating dependencies to multiple fixtures.
def test_login_user(client, test_user):
    # Field for login is "username" and not "email".
    res = client.post(
        "/login", data={"username": test_user["email"], "password": test_user["password"]})

    # Spreading the pydantic dict, to access all fields, and avoid specifying each field
    login_res = schemas.Token(**res.json())  # Validating response
    # Decoding the access token in order to verify it, and allow only the rightful user with the correct credentials. Algorithm must be in a list.
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    # The user_id is from the access token in the auth module, when creating access token with oauth. The user id is something customly wanted to be retrieved.
    id = payload.get("user_id")

    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200  # OK.


# First parameter, testing for these fields. Second argument, an array with tuples of different tests wished to be ran.
@pytest.mark.parametrize("email, password, status_code", [
    ("email@not.correct", "1", 403),  # Wrong email, correct password
    ("1@1.com", "wrong_passawordio", 403),  # Correct email, wrong password
    ("email@not.correct", "wrong_passawordio", 403),  # Wrong email wrong password
    (None, "1", 422),  # No email, correct password
    ("1@1.com", None, 422)  # Correct email, no password
])
def test_incorrect_login(client, email, password, status_code):  # Pass in the parameters
    res = client.post(
        "/login", data={"username": email, "password": password})  # Testing for wrong credentials.
    assert res.status_code == status_code
