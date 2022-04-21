from pydantic import BaseModel, EmailStr  # For email field
from pydantic.types import conint
from datetime import datetime  # For use in field of created_at

# For providing optional ID field in the Token Data payload.
from typing import Optional

# Extending from Pydantic, Basemodel. Used for defining the construction of a post when receiving POST request from the frontend.
# A Pydantic schema defines the structure of a request and response. This ensures that when a post is created, the request will only go through if the defined fields are included.


class PostBase(BaseModel):
    """
    This is a base class extending from BaseModel. This class is used to define a pydantic schema, so as to allow all
    sub-classes to extend from. This schema contains all fields which must be provided in all classes extending from this class.
    If any additional fields are desired, they must be specified in addition in each child-class when inheritting from this base class.
    """
    title: str  # The fields defined for receiving data.
    content: str  # May be as many or few fields are desired.
    # followers: int
    # Let's the user decide if the post should be published. If no value is provided from user, it evaluates to True and is posted (sent).
    published: bool = True
    # Takes an extra argument in whatever type neccesary for the field. This field is optional - if the user does not provide anything, it will default to None and not be posted.
    # rating: Optional[int] = None


class PostCreate(PostBase):
    """
    This is a class for creating posts. This class extends from the PostBase class defined as the base class for posts.
    This handles the way posts must be constructed when sent from the user.
    """
    pass


# Response class made to avoid sending back the user password, when a request is being made.
class UserOut(BaseModel):
    """
    This is the response sent back to the client, when a request to "User" has been made - whenever a new user is created, this is returned.
    """
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    """
    This is a class for handling data when data is sent to the user. A response.
    This class extends from the custom defined PostBase class.
    """
    id: int
    created_at: datetime
    users_id: int
    # Returned as a dict. Sending UserOut also, since the name/username/owner of the post is wanted attached for each post, and not just their user id.
    owner: UserOut  # Owner is defined as a property in the "Post" schema.

    # This must be specified in this response class, much like metadata, since the data is NOT a dict.
    # Pydantic needs this config and is forced to read it as it is, as Pydantic only reads dicts - because ORMs are not dicts.
    class Config:
        orm_mode = True


class PostVotes(BaseModel):
    """
    This is a class for displaying the needed and desired fields corretly, when retrieving a post with its upvotes attached.
    """
    # Pydantic expects the fields specified as such. This field is returned capitalized when accessed in e.g. Postman.
    # This is a reference to the class schema "Post" with all of its fields included.
    Post: Post  # Capital "P" is expected.
    votes: int

    # This must be specified in this response class, much like metadata, since the data is NOT a dict.
    # Pydantic needs this config and is forced to read it as it is, as Pydantic only reads dicts - because ORMs are not dicts.
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """
    This is a schema for when creating a new user. The user must provide specified fields, when creating a user.
    The "email-validator" library will ensure when the user enters an email, it's a valid email. "EmailStr" is imported from "pydantic".
    """
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    This is a schema for when users post a request to provide login credentials.
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    This is a schema for ensuring tokens match accordingly.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    This is a schema for the token data. Making sure the embedded into the access token.
    """
    id: Optional[str] = None  # Is optional.


class Vote(BaseModel):
    """
    This is a schema for voting and ensures validation of votes and voters.
    """
    post_id: int

    # This field is used for defining the direction of votes. Either the direction is 0 or it's 1 - meaning either it's a downvote or an upvote.
    # To ensure either 0 or 1 is passed in as values, the conint type is used, and set to Less than or Equal to 1 (le=1). This however allows negative numbers.
    dir: conint(le=1)
