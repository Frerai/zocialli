import pytest
from app import schemas

# Dependant on fixtures in conftest.py. Testing for getting all posts.
# Users must be authorized and test posts must be created first, which is handled in conftest.


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    # Testing if number of retrieved posts matches the number of created test posts .
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200  # OK.


# Client is a non-logged in user, who doesn't have authorized credentials
def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401  # Unauthorized.


# Client is a non-logged in user, who doesn't have authorized credentials
def test_unauthorized_user_get_one_particular_post(client, test_posts):
    # Simply grabbing the first test post.
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401  # Unauthorized.


# Testing for a wrong post id with authorized access.
def test_get_one_post_with_wrong_id(authorized_client, test_posts):
    # Hardcoding id to make sure it doesn't exist.
    res = authorized_client.get(f"/posts/89478956165")
    assert res.status_code == 404  # Not Found.


def test_get_one_post(authorized_client, test_posts):
    # Getting the id of first post.
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    # Res must be unpacked as json in order to access each field in the dict. Validating, to make sure all fields in the post are passed in.
    # This will allow to access each field in the custom created pydantic model and compare those field to the test posts.
    post = schemas.PostVotes(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


@pytest.mark.parametrize("title, content, published", [
    ("Testing first title",
     "This is the first test content for creating posts with authorized user", True),
    ("Testing second title",
     "This is the SECOND test content for creating posts with authorized user", False),
    ("Testing third title",
     "This is the thridly test content for creating posts with authorized user", False),

])
# Testing for creating one post with an authorized user.
def test_create_post(authorized_client, test_user, title, content, published):
    # Data for the post.
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published})
    # Performing validation to ensure correct and all fields are passed in.
    created_post = schemas.Post(**res.json())

    assert res.status_code == 201  # Created.
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    # Ensuring the same user created the post.
    assert created_post.users_id == test_user["id"]


# Client is a non-logged in user, who doesn't have authorized credentials and is creating a post.
@pytest.mark.parametrize("title, content", [
    ("Testing first title",
     "This is the first test content for creating posts with UNauthorized user"),
    ("Testing second title",
     "This is the SECOND test content for creating posts with UNauthorized user"),
    ("Testing third title",
     "This is the thridly test content for creating posts with UNauthorized user"),

])
def test_unauthorized_user_create_post(client, test_posts, title, content):
    res = client.post(  # Using a post method.
        "/posts/", json={"title": title, "content": content})
    assert res.status_code == 401  # Unauthorized.


# Client is an unauthorized user trying to delete a particular post.
def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(  # This is a delete method.
        f"/posts/{test_posts[0].id}")
    assert res.status_code == 401  # Unauthorized.


# Client is an authorized user, and wants to delete own post.
def test_authorized_user_delete_own_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(  # This is a delete method.
        f"/posts/{test_posts[0].id}")
    assert res.status_code == 204  # No Content.


def test_authorized_user_delete_own_post_with_wrong_post_id(authorized_client, test_user, test_posts):
    res = authorized_client.delete(  # This is a delete method.
        f"/posts/655647988468479")  # ID set to something wrong.
    assert res.status_code == 404  # Not Found.


def test_authorized_user_delete_other_users_post(authorized_client, test_user, test_posts):
    # Trying to delete the post of index 3s id, which is created by test_user_two, and the authorized client is logged in for test user 1.
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403  # Forbidden.


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "testing update",
        "content": "Testing updates for authorized user and own post",
        "id": test_posts[0].id

    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 202  # Accepted.
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_update_other_user_post(authorized_client, test_user, test_user_two, test_posts):
    data = {
        "title": "testing updates",
        "content": "An authorized user is updating another users post",
        # Test user 2s post, but logged in as test user 1.
        "id": test_posts[3].id

    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403  # Forbidden.


# An unauthorized user updating a post.
def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(  # Put method.
        f"/posts/{test_posts[0].id}")
    assert res.status_code == 401  # Unauthorized.


def test_authorized_user_update_own_post_with_wrong_id(authorized_client, test_user, test_posts):
    data = {
        "title": "testing updates",
        "content": "Test for an authorized user to updating a post with wrong id.",
        "id": test_posts[3].id

    }
    res = authorized_client.put(
        f"/posts/89494654889", json=data)  # Wrong ID.

    assert res.status_code == 404  # Not Found.
