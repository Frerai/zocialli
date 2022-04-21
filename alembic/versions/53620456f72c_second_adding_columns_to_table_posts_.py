"""Second. Adding columns to table posts: content

Revision ID: 53620456f72c
Revises: 2f8536fd8692
Create Date: 2022-04-20 18:32:40.419155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53620456f72c'
down_revision = '2f8536fd8692'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade():
    # Downgrade logic HAS to be provided every time upgrade logic is applied.
    # Dropping from "posts" table, name of the column "content".
    op.drop_column("posts", "content")
    pass
