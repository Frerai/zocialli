from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

# From 2 directories above, import modules.
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # Querying for the post based on Post id and compare with the votes post_id to ensure the post exists, before being able to upvote/downvote it.
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with no. {vote.post_id} does not exist")

    # Building up the query, and not actually performing it here.
    # Querying to see if the vote/like already exists or not - if the user has or has not already voted to avoid multiple upvotes on same post.
    # Taking "Vote" table, and filtering the tables' "post_id" column to compare the id of the post_id entered.
    # Entering second criteria to ensure the voters user_id entered is the same as the current authenticated user.
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    found_vote = vote_query.first()
    # If the user wants to like a post, but the upvote already exists, the user won't be permitted to upvote again.
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.email} has already upvoted post {vote.post_id}")
        # If the vote wasn't found, then create a new upvote on the post.
        # The post_id field of Vote table is going to be set to vote.post_id entered in by the user.
        # Then grabbing the user_id field and setting the id to the currently authenticated and logged in users id.
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)  # Adding the vote to the db.
        db.commit()
        return {"message": "<3 You have liked this post <3"}
    else:
        if not found_vote:  # If vote.dir is 0, meaning the user wants to remove an upvote.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="You haven't upvoted this post yet")

        # If the vote/like was found, delete it.
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "</3 You no longer like this post </3"}
