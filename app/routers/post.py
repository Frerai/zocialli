# For using HTTP statuscodes. Raising HTTP exceptions. For creating a response, Using Depends to bind Session to the DB object. APIRouter to route the API instance.
from fastapi import status, HTTPException, APIRouter, Response, Depends

# From 2 directories up, import models and schemas module from the respective directories and all of their content.
from .. import models, schemas, oauth2
from ..database import get_db  # For opening/closing connection to DB.
# For creating dependency with a user when creating a post. A user must be logged in before creating a post.
from ..oauth2 import get_current_user

from sqlalchemy.orm import Session  # For establishing a connectivity session.
from sqlalchemy import func  # Enables function "count" for GROUP BY clause.

# For use of optional fields. For use in returning all posts, in a list, as one post.
from typing import Optional, List


# Routing from this, using the APIRouter. These routes will be referenced in the main file.
router = APIRouter(
    # The prefix wanted to be included in all of the paths. This prefix allows it to be removed from each path function.
    prefix="/posts",
    tags=["Posts"]  # This will add a group named "Posts" in swaggerUI.
)


# Decorator turns the function into a PATH operation (a route). Anyone using this API can access this endpoint.
# Response must be wrapped in this List, so as to return all the posts in 1 list. Or it won't return anything.
@router.get("/", response_model=List[schemas.PostVotes])  # Posts + votes
# First accessing the "db" object, that creates a session to the DB via "get_db".
# Anytime ORM queries to the DB is being made, the dependency must be passed in the path operation function to create a dependency.
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 25, skip: int = 0, search: Optional[str] = ""):
    '''
    Using SQL statements to make queries to the DB with the database drive:
    # Using the instance "cursor" to execute SQL statement.
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()  # The fetchall method will run the statement, and is used to retrieve multiple posts. Storing the output in a variable.
    '''
    # Use the query method to make a query to the desired model/table. "all()" queries all of the table content. Limit provides an optional limit on how many results to return.
    # Providing optional query parameters like search, that checks if the table Post has anything containing the search in its Title.

    # posts = db.query(models.Post).filter(
    #     models.Post.title.contains(search)).limit(limit).offset(skip).all()  # Also providing Limit and Offset as query parameters.

    # Returning the data which is stored in the DB. FastAPI automatically converts it into JSON.
    # Specifying the table to join, and then the column to do the join on. SQLAlchemy default join is LEFT INNER JOIN, so outer param must be specified.
    # Using Count function, to count the post_id column as "votes", in the GROUP BY clause. LEFT OUTER joining on post id.
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


# 2nd param overriding the default statuscode of 200 with 201. Within the decorator the response model must be specified like below.
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''
    # Inserting the values as parameters. "%s" represents a variable, and should function as placeholders for the values wanting to be entered.
    # The columns wanting to be inserted must then be provided as second parameter, each column specified. Columns are grabbed from the body of "post".
    cursor.execute(
        """INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *""", (post.title, post.content))  # Values may be entered i.e via Postman.
    new_post = cursor.fetchone()
    # Statement must be commited in order for changes and updates to take effect.
    conn.commit()
    '''
    # Creating a post, using the model of Post, and accessing desired columns.
    """ new_post = models.Post(**post.dict()) is a pydantic model, and this will allow to unpack all the fields in the table model and only pass in the values in i.e Postman,
    in case the table has like 50 fields that each needs to be specified individually like below in title=post.title, content=post.content etc."""
    # Since **post.dict just spreads out the schema from the body, and users_id is NOT a field that needs(or wants) to be provided in the schema,
    # users id must be retrieved from the current_user fuctions id field. As users_id is not a field in the schema, it must be specified here.
    new_post = models.Post(users_id=current_user.id, **post.dict())
    db.add(new_post)  # Must be specified to add changes to DB.
    db.commit()  # Must be specified to commit changes to DB.
    db.refresh(new_post)  # Works like SQL "RETURNING" statement.
    return new_post


# Retreiving one particular post.
@router.get("/{id}", response_model=schemas.PostVotes)
# Performing a validation to ensure data entigrity.
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id))
                   )  # To avoid any attacks, a placeholder is entered - placeholder may be modified using i.e. Postman. Must be converted back as a str, to show content, or it won't be able to be indexed.
    # Must be used to return whatever SQL statement is passed in above.
    post = cursor.fetchone()'''
    # Use the filter method to retrieve one particullar post, rather than querying for all the posts. This is equivalent to the WHERE clause in SQL.
    # First method is used when the first entry is found and Postgres shouldn't look for all or other entries. This is used i.e. when looking for specific IDs like a PK.

    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:  # If no post was found.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,  # Referencing only, not creating an object.
                            detail=f"post with id {id} does not exist")  # 2nd param is the message. Raising an exception.
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''
    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()  # To get the deleted post.
    conn.commit()  # Commiting the changes to the DB.
    '''
    # First defining the query to search for the post to be deleted.
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()  # Then finding the actual post.

    # Checking if post doesn't exists.
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id: {id} does not exist")

    # Users id must be the currently logged in users id, in order to be able to delete posts! Otherwise, the user is allowed to delete ALL posts.
    if post.users_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are NOT allowed to perform this action")

    # Grabbing the ORIGINAL query for the post. Deleting the post.
    post_query.delete(synchronize_session=False)  # This is default.
    db.commit()  # Committing changes to the DB.

    # This ensures the proper response, since no data should be sent back when returning status code 204.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''
    cursor.execute("""UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()'''
    # Not running the query, just saving the query to variable.
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()  # Grabbing first post, if it exist.

    # Sending a meaningful error message, rather than "Internal Server Error".
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id: {id} does not exist")

    # Users id must be the currently logged in users id, in order to be able to update posts - otherwise, the user is allowed to update ALL posts.
    if post.users_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are NOT allowed to perform this action")

    # Chaining update method to the query run at first instance. Using the post schema, and return it as a dict, so that entries and columns doesn't get hardcoded here.
    # This will allow any desired value to be updated from i.e. Postman, without having to specify the value and entry here as hardcode.
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    # Running a query from the exact post_query object, and grabbing the first entry to modify.
    return post_query.first()
