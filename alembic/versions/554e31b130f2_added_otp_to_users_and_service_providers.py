"""added otp to users and service providers

Revision ID: 554e31b130f2
Revises: cc4cabec3178
Create Date: 2024-06-20 16:22:22.815838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '554e31b130f2'
down_revision: Union[str, None] = 'cc4cabec3178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('serviceProvider', sa.Column('otp', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('otp', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'otp')
    op.drop_column('serviceProvider', 'otp')
    # ### end Alembic commands ###
