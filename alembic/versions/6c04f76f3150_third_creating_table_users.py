"""Third. Creating table: users

Revision ID: 6c04f76f3150
Revises: 53620456f72c
Create Date: 2022-04-20 19:18:07.713244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c04f76f3150'
down_revision = '53620456f72c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("email", sa.String, nullable=False),
                    sa.Column("password", sa.String, nullable=False),
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                              server_default=sa.text("now()"), nullable=False),
                    # This is another way of setting a PK. Use the PrimaryKeyConstraint class, and specify the column name.
                    sa.PrimaryKeyConstraint("id"),
                    # Ensures no duplicates may be entered on the specified column.
                    sa.UniqueConstraint("email")
                    )
    pass


def downgrade():
    op.drop_table("users")
    pass
