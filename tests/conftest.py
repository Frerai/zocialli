# File for defining fixtures. Usage for Pytest.
import pytest
from fastapi.testclient import TestClient

from app.main import app  # The main FastAPI instance, app.

from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Decorator allows for a list of parameters wanting to be tested for. A list of expected results must be provided.
# @pytest.mark.parametrize()


# First, type of database. Second, username (default is "postgres"). Third, password. Fourth, IP address. Fifth, port number. Sixth, database name.
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@\
{settings.database_hostname}:{settings.database_port}/{settings.database_name}_tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Overriding the SessionLocal to a test session for test environment purposes. From the FastAPI documentation.
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Creating an instance of TestClient from the FastAPI instance.
# client = TestClient(app) # This may also be set as a fixtures, to then be returned instead.


# Fixture for yielding the Database object. Used to create dependencies across fixtures.
# This still allows for data to be manipulated, by passing "session" in the request.
# Scope will run once per whatever level chosen - once per function will run fixture before each test function is run.
@pytest.fixture(scope="function")
def session():
    # The tables are dropped FIRST before anything else. This avoids redundancies of entering unique values for each test.
    Base.metadata.drop_all(bind=engine)

    # This is enough to create all the tables defined in app.models. When pytest runs first time, this ensures all schemas are created.
    # This allows to create clean new tables to be populated, since the tables were first dropped, AFTER returning the TestClient.
    Base.metadata.create_all(bind=engine)

    # This returns the DB object and allows to make queries to it.
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fixture. A function that runs before the actual tests. This allows to use values in multiple places.
# This returns the client and not the DB object.
@pytest.fixture(scope="function")
def client(session):  # Dependency to session.

    # This overrides the dependencies, and allows for the sessionmaker to point to a new test DB for ALL the functions with the regular
    # "db: Session = Depends(get_db)" setting, without having to change each of those dependencies manually. From FastAPI Documentation.
    def override_get_db():
        try:
            yield session  # Yielding session rather than "db".
        finally:
            session.close()

    # Overrides the dependencies of get_db instance with the test db. From FastAPI documentation. Basically swaps the dependencies out.
    app.dependency_overrides[get_db] = override_get_db
    # Runs the tests and populates clean tables, which allows for unique entries to be repeated.
    yield TestClient(app)


# Fixture for creating a test user for testing purposes.
@pytest.fixture
def test_user(client):  # Making request to client to access session.
    user_data = {"email": "1@1.com", "password": "1"}

    # Sending request to users api endpoint. Data for new user.
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201  # Created.
    new_user = res.json()  # Getting the dictionary.
    # Taking password from user_data and setting it to new_user password to match credentials.
    new_user["password"] = user_data["password"]

    # This allows to pass in required fields into other tests dependent of this fixture, even if test user credentials are changed here.
    return new_user


# Fixture for creating a test user for testing purposes.
@pytest.fixture
def test_user_two(client):  # Making request to client to access session.
    user_data = {"email": "2@2.com", "password": "2"}

    # Sending request to users api endpoint. Data for new user.
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201  # Created.
    new_user = res.json()  # Getting the dictionary.
    # Taking password from user_data and setting it to new_user password to match credentials.
    new_user["password"] = user_data["password"]

    # This allows to pass in required fields into other tests dependent of this fixture, even if test user credentials are changed here.
    return new_user


@pytest.fixture
# For creating a token. Dependent on creating a test user first.
def token(test_user):
    # Pass in the users id in a dict from test_user. This returns a token.
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {  # Updating the headers to match correct credentials and gain access.
        **client.headers,  # Spreading out all current headers.
        # Adding an extra header. Need Bearer first.
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture  # Creating posts in the DB for testing purposes.
def test_posts(test_user, test_user_two, session):
    posts_data = [{
        "title": "First test",
        "content": "This is the first content for first test",
        "users_id": test_user["id"]
    }, {
        "title": "Second test",
        "content": "This is the second content for second test",
        "users_id": test_user["id"],
    },
        {
        "title": "Third test",
        "content": "This is the third content for third test",
        "users_id": test_user["id"],
    },
        {
        "title": "first test for user 2",
        "content": "This is the first content for test user 2t",
        "users_id": test_user_two["id"],
    }]

    # Function for reading the posts_data dict, and passing in each KV pair to be read. Converts dictionary into a post model.
    def create_post_model(post):
        return models.Post(**post)  # Simply taking post, and spreading it.

    # Takes a (custom) function and iterates the passed in data. Will convert the data into a map.
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)  # Map must be converted to a list.

    # The add_all method adds multiple entries of data to the DB at the same time. A list must be passed in of the Post model.
    # Since the data has been converted from a dict to map to a list, it can be passed in directly like this.
    session.add_all(posts)

    session.commit()
    posts = session.query(models.Post).all()
    return posts
