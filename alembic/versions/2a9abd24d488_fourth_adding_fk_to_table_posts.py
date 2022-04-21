"""Fourth. Adding FK to table: posts

Revision ID: 2a9abd24d488
Revises: 6c04f76f3150
Create Date: 2022-04-20 19:38:19.595572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a9abd24d488'
down_revision = '6c04f76f3150'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("user_id", sa.Integer(), nullable=False))
    # First is an arbitrary name for the FK. Second is source table of the FK. Third is the table of reference.
    # Fourth is the column in the source table wanted to be used. Fifth is the column referenced to.
    op.create_foreign_key(
        "post_users_fk", source_table="posts", referent_table="users", local_cols=["user_id"], remote_cols=["id"], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint("post_users_fk", table_name="posts")
    op.drop_column("posts", "user_id")
    pass
