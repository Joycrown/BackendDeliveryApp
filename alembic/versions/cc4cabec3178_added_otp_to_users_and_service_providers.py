"""added otp to users and service providers

Revision ID: cc4cabec3178
Revises: 516edf785438
Create Date: 2024-06-20 16:17:33.141780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc4cabec3178'
down_revision: Union[str, None] = '516edf785438'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
   pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'otp')
    op.drop_column('serviceProvider', 'otp')
    # ### end Alembic commands ###