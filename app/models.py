# Module for defining models for creating tables.

# For defining the columns via ORM (object-relational mapping).
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship

from .database import Base  # Model for defining and creating tables.


# Class for posting posts. Extends from Base model from SQLalchemy.
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    # Server default must be provided, if a default value is desired.
    published = Column(Boolean, nullable=False, server_default="TRUE")
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))  # Needed for adding current time and timezone.
    # Use the table name you want to establish a relation to, not the class name. The column of the foreign table.
    users_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    # This returns the class of another model. Not the table.
    # This creates a property for each retrieved post, and returns an owner for each post. This just figures out the relationship to User class.
    # Must be included as a field in the returned schema.
    owner = relationship("User")


# Class for creating a table in Postgres for user registration.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)  # Unique constraint.
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))  # Needed for adding current time and timezone.
#    name = Column(String, nullable=False)


class Vote(Base):
    __tablename__ = "votes"

    # Using the ForeignKey method from SQLAlchemy to set the columns as composite keys.
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True)
