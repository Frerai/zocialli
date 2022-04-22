from pydantic import BaseSettings


class Settings(BaseSettings):
    """A class for creating settings and environment variables for this app to run. Settings and environment variables are then validated before running.
    """
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Using the built-in "Config" class of Pydantic, telling Pydantic to import the values from where these are set.
    class Config:
        env_file = ".env"


settings = Settings()
