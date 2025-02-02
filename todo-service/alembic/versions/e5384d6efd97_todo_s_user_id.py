"""Todo's user_id

Revision ID: e5384d6efd97
Revises: 278ba0e9c2ed
Create Date: 2025-01-14 10:09:09.579944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e5384d6efd97'
down_revision: Union[str, None] = '278ba0e9c2ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_todo_user_id'), 'todo', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_todo_user_id'), table_name='todo')
    op.drop_column('todo', 'user_id')
    # ### end Alembic commands ###
