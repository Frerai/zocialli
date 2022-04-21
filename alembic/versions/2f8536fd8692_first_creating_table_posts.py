"""First. Creating table: posts

Revision ID: 2f8536fd8692
Revises: 
Create Date: 2022-04-20 18:13:18.613492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f8536fd8692'
down_revision = None
branch_labels = None
depends_on = None


#  This will run the commands for making desired changes. All logic for making said changes must be passed into this function.
def upgrade():
    # Accessing "op" object of Alembic to create a table. Take the sa (SQLAlchemy) object, and set up the needed columns.
    op.create_table("posts", sa.Column(
        "id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False)
    )
    pass


# This function will do a rollback to all the changed previously made. The logic of desired (un)change must be passed into this function.
def downgrade():
    op.drop_table("posts")
    pass
