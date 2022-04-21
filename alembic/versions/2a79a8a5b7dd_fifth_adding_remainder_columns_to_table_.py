"""Fifth. Adding remainder columns to table: posts

Revision ID: 2a79a8a5b7dd
Revises: 2a9abd24d488
Create Date: 2022-04-20 19:53:39.450226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a79a8a5b7dd'
down_revision = '2a9abd24d488'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts",
                  sa.Column(
                      "published", sa.Boolean(), nullable=False, server_default="TRUE"))
    op.add_column("posts",
                  sa.Column("created_at", sa.TIMESTAMP(
                      timezone=True), nullable=False, server_default=sa.text("now()"))
                  )
    pass


def downgrade():
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
    pass
