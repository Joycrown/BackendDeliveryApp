"""adding payment Intent table

Revision ID: 6ec2845f2cf3
Revises: ba03098eaf23
Create Date: 2024-05-23 14:17:25.676787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ec2845f2cf3'
down_revision: Union[str, None] = 'ba03098eaf23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_intents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('customer_email', sa.String(), nullable=False),
    sa.Column('transporter_email', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment_intents')
    # ### end Alembic commands ###