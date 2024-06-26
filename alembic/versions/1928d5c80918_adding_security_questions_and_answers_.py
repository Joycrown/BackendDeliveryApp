"""Adding security questions and answers to users and service provider

Revision ID: 1928d5c80918
Revises: 19a72bcce2a2
Create Date: 2024-06-22 16:54:49.132227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1928d5c80918'
down_revision: Union[str, None] = '19a72bcce2a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('serviceProvider', sa.Column('security_question_1', sa.Text(), nullable=True))
    op.add_column('serviceProvider', sa.Column('security_answer_1', sa.String(), nullable=True))
    op.add_column('serviceProvider', sa.Column('security_question_2', sa.Text(), nullable=True))
    op.add_column('serviceProvider', sa.Column('security_answer_2', sa.String(), nullable=True))
    op.add_column('serviceProvider', sa.Column('security_question_status', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('security_question_1', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('security_answer_1', sa.String(), nullable=True))
    op.add_column('users', sa.Column('security_question_2', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('security_answer_2', sa.String(), nullable=True))
    op.add_column('users', sa.Column('security_question_status', sa.Boolean(), server_default='false', nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'security_question_status')
    op.drop_column('users', 'security_answer_2')
    op.drop_column('users', 'security_question_2')
    op.drop_column('users', 'security_answer_1')
    op.drop_column('users', 'security_question_1')
    op.drop_column('serviceProvider', 'security_question_status')
    op.drop_column('serviceProvider', 'security_answer_2')
    op.drop_column('serviceProvider', 'security_question_2')
    op.drop_column('serviceProvider', 'security_answer_1')
    op.drop_column('serviceProvider', 'security_question_1')
    # ### end Alembic commands ###
