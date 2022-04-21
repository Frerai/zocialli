# For using HTTP statuscodes. Raising HTTP exceptions. Using Depends to bind Session to the DB object. APIRouter to route the API instance.
from fastapi import status, HTTPException, Depends, APIRouter

# From 2 directories up, import models and schemas module from the respective directories and all of their content.
from .. import models, schemas, utils
from ..database import get_db  # For opening/closing connection to DB.

from sqlalchemy.orm import Session  # For establishing a connectivity session.


# Routing from this, using the APIRouter. These routes will be referenced in the main file.
router = APIRouter(
    # Prefix will add path to each route, and allow to remove that specified path in each function related to the route.
    prefix="/users",
    tags=["Users"]  # Grouping these operations together in SwaggerUI.
)


# Using the custom defined response model to specify which fields to return as response, when a request is made to User. This avoids returning the user password.
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # First calling the custom defined hash function, which performs a hash. Pass in the column to be hashed, which is "password" in user schema.
    hashed_password = utils.hash(user.password)
    user.password = hashed_password  # Setting the column to hashed_password.

    # Unpacking all fields from "user.dict".
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Must use response model, with the correct schema, to have the response do as desired. To i.e leave out any custom fields like passwords.
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    # Querying User table and filtering to look for the user ID.
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user
