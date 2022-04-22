from pydantic import BaseSettings


class Settings(BaseSettings):
    """A class for creating settings and environment variables for this app to run. Settings and environment variables are then validated before running.
    """
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Using the built-in "Config" class of Pydantic, telling Pydantic to import the values from where these are set.
    class Config:
        env_file = ".env"


settings = Settings()
