"""adding rejected service provider to orders

Revision ID: 7fecf8316658
Revises: 0e8a7082dbce
Create Date: 2024-05-06 17:24:10.735113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fecf8316658'
down_revision: Union[str, None] = '0e8a7082dbce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rejectedOrder', sa.Column('status', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rejectedOrder', 'status')
    # ### end Alembic commands ###
