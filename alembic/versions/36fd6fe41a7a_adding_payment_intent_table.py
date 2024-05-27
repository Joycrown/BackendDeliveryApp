"""adding payment Intent table

Revision ID: 36fd6fe41a7a
Revises: 1ce289e1c729
Create Date: 2024-05-21 14:21:01.679240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36fd6fe41a7a'
down_revision: Union[str, None] = '1ce289e1c729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_intents_id'), table_name='payment_intents')
    op.drop_table('payment_intents')
    # ### end Alembic commands ###