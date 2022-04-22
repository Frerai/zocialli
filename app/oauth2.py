# Module for creating JWT - for authentication purposes.

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

# For generating tokens and handling their expiration time.
from datetime import datetime, timedelta

from sqlalchemy.orm import Session


from . import schemas, models
from .database import get_db
from .config import settings

# The endpoint for the login endpoint must be provided here. The router/path without providing "/".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Default setting, long string from documentation.
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm  # Default setting from documentation.
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Data will be encoded into the token. It will be passed in as a variable of type dict.
def create_access_token(data: dict):
    # Data is just supposed to be copied, since it's going to be encoded into the JWT.
    to_encode = data.copy()

    # Takes the current time, and adds the time set as when the token must expire.
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Adding an extra property of expiration time, to all of the data wanted to be encoded as the JWT.
    to_encode.update({"exp": expire})  # Will show expiration time.

    # First is everything wanted to be put into the payload. Second is secret key. Third is the algorithm.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        # Decoding the access token in order to verify it, and allow only the rightful user with the correct credentials. Algorithm must be in a list.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # The user_id is from the access token in the auth module, when creating access token with oauth. The user id is something customly wanted to be retrieved.
        id: str = payload.get("user_id")

        if id is None:
            # Raising whatever exceptions provided in the function is being raised here.
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data  # Returns the id pretty much.


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    # Querying to match the id in the verified token to the users id stored in the DB to return the id to the user IF they match. As a service.
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
