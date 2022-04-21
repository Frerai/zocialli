from fastapi import FastAPI
# By default the webbrowser domain and this APIs server domain can only connect with eachother, when they are on the same domain.
# This CORS (Cross Origin Resource Sharing) middleware allows webbrowsers on other domains to send requests to this API endpoints domain.
from fastapi.middleware.cors import CORSMiddleware

from .routers import post, user, auth, vote


# This is used to create all of the models used for defining and creating tables in the Postgres DB via ORM (object-relational mapping).
# This command tells SQLAlchemy to run the create satatement, to generate all of the tables defined in the models module, when first starting up.
# models.Base.metadata.create_all(bind=engine) Not needed, since Alembic is used.


app = FastAPI()  # Creating an instance.
"""Commands for running the webserver:
'uvicorn "name_of_file":"name_of_FastAPI_instance"'
'uvicorn "name_of_file":"name_of_FastAPI_instance" --reload' will watch for changes in the directory, which allows to reload the server, whenever any changes has been made to the code.
'uvicorn app.main:app --reload' specifically to run this particullar module and app.
"""

# Specify the domains allowed to send requests to this API and all of its endpoints.
origins = ["*"]

# Default settings from FastAPI official documentation.
app.add_middleware(
    # Middleware. It's a function that runs before every request.
    CORSMiddleware,
    # Domains allowed to talk to/send requests to this API.
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # The HTTP methods allowed to use on this API.
    allow_headers=["*"],  # The headers allowed to use on this API.
)


# Importing the router object from "post" and "user", and including all routes defined in both modules, in here.
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def main():
    return {"message": "Hello World"}
