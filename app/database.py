import psycopg2  # Postgres adapter - for connecting to the Postgres DB.
# For returning the column names when making a query - psycopg does NOT include these names by default, so this method provides those names and not only values of these columns.
from psycopg2.extras import RealDictCursor
import time  # For putting a delay on re-attempting connectivity to DB.


# Imports needed when running the script with SQLAlchemy.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# First, type of database. Second, username (default is "postgres"). Third, password. Fourth, IP address. Fifth, port number. Sixth, database name.
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# When wanting to interact with the SQL database, a sessionmaker must be created. Arguments are default arguments.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The base class for all the models defined to create tabels in Postgres and will be extending from this "Base" class.
Base = declarative_base()


# Default settings taken from FastAPI documentation. This is a dependency.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


'''DOCUMENTATION PURPOSES:
This is only used, when wanting to run raw SQL directly using "psycopg2" postgres library to acces the DB, instead of SQLAlchemy.'''
# Continously run, and break if connection to DB is compromised. Server must not run, if DB cannot be accessed.
while True:
    try:
        # First parameter is the host (IP adress), second is the database wanting to connect to (), third is the user wanted to
        # connect as (default name is "postgres"), fourth is user password, fifth is a cursor which is used for mapping the column names to correct column values.
        conn = psycopg2.connect(host=settings.DATABASE_HOSTNAME, database=settings.DATABASE_NAME, user=settings.DATABASE_USERNAME,
                                password=settings.DATABASE_PASSWORD, cursor_factory=RealDictCursor)

        # Opens a cursor to perform database operations. Calls the cursor method and saves it in the variable.
        cursor = conn.cursor()
        print("Database connection was successfully established")
        break  # If Database connection is successful, break out of loop. This is a precaution to ensure connection to DB is established before running server.
    # Getting the error, and storing it in the variable "error".
    except Exception as error:
        print("Connection to database failed")
        print("Error:", error)
        # Putting a delay of x seconds before re-attempting to establishing connection to DB.
        time.sleep(3)
