"""Create individual challenges table

Revision ID: 82d9c780e3c3
Revises: 
Create Date: 2023-12-04 23:46:45.964960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82d9c780e3c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(op=None):
    op.create_table(
        "individual_challenge_model",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hmackey", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["challenges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade(op=None):
    op.drop_table("individual_challenge_model")
    pass
