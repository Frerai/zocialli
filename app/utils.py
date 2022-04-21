# Module for holding utility functions such as hashing passwords.

# Used for hashing and verifying passwords, encrypting them when storing them to DB so they won't appear as plain text.
from passlib.context import CryptContext

# This setting tells passlib the default hashing algorithm to use (bcrypt).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


# Function for verifying provided pw to the hashed pw, in order to authenticate a user and their provided login credentials.
def verify(plain_password, hashed_password):
    # The "verify" method will do the comparison logic.
    return pwd_context.verify(plain_password, hashed_password)
