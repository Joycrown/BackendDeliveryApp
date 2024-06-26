"""creating a budget table

Revision ID: 2ac0d805f236
Revises: 7263c2838339
Create Date: 2024-04-22 16:24:27.320008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ac0d805f236'
down_revision: Union[str, None] = '7263c2838339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('budgets',
    sa.Column('budget_id', sa.String(), nullable=False),
    sa.Column('service_provider_id', sa.String(), nullable=False),
    sa.Column('order_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.Date(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['service_provider_id'], ['serviceProvider.service_provider_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('budget_id'),
    sa.UniqueConstraint('budget_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('budgets')
    # ### end Alembic commands ###
