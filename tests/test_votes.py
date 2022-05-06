import pytest
from app import models


# Fixture for creating a vote on a post from a particular user.
@pytest.fixture()
def test_vote(test_posts, session, test_user):
    # Columns needed from the Vote table.
    vote = models.Vote(post_id=test_posts[0].id, user_id=test_user["id"])
    session.add(vote)
    session.commit()


# Authorized as user 1, and upvoting on own post.
def test_vote_on_post_successfully(authorized_client, test_posts):
    res = authorized_client.post(
        f"/votes/", json={"post_id": test_posts[0].id, "dir": 1})  # Dir 1 is upvoting.
    assert res.status_code == 201  # Created.


# Trying to upvote the same post twice.
# Dependant on the fixture "test_vote" which ensures the particular user alread has casted an upvote on a particular post.
def test_vote_twice_on_same_post(authorized_client, test_posts, test_vote):
    res = authorized_client.post(
        f"/votes/", json={"post_id": test_posts[0].id, "dir": 1})  # Dir 1 is upvoting.
    assert res.status_code == 409  # Conflict.


# Removing a vote.
def test_remove_vote(authorized_client, test_posts, test_vote):
    res = authorized_client.post(
        f"/votes/", json={"post_id": test_posts[0].id, "dir": 0})
    assert res.status_code == 201  # Created.


# The vote doesn't exist, and test_vote is not being used here. Authorized user is trying remove their vote from a non-existing vote.
def test_remove_vote_not_already_existing(authorized_client, test_posts):
    res = authorized_client.post(
        f"/votes/", json={"post_id": test_posts[0].id, "dir": 0})
    assert res.status_code == 404  # Not Found.


# Voting on a post that doesn't exist.
def test_vote_on_non_existing_post(authorized_client, test_posts):
    res = authorized_client.post(
        f"/votes/", json={"post_id": 8945879878, "dir": 1})
    assert res.status_code == 404  # Not Found.


# Testing an authorized user trying to upvote/down on a post.
def test_unauthorized_user_vote_on_post(client, test_posts):
    res = client.post(
        f"/votes/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 401  # Unauthorized.
