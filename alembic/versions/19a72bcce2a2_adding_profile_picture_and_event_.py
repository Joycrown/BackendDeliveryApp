"""Adding profile picture and event listeners to users and service provider

Revision ID: 19a72bcce2a2
Revises: 78786f20e9b0
Create Date: 2024-06-21 19:10:40.809473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19a72bcce2a2'
down_revision: Union[str, None] = '78786f20e9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('serviceProvider', sa.Column('profile_picture', sa.String(), server_default='N/A', nullable=False))
    op.add_column('serviceProvider', sa.Column('email_is_verified', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('profile_picture', sa.String(), server_default='N/A', nullable=False))
    op.add_column('users', sa.Column('email_is_verified', sa.Boolean(), server_default='false', nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'email_is_verified')
    op.drop_column('users', 'profile_picture')
    op.drop_column('serviceProvider', 'email_is_verified')
    op.drop_column('serviceProvider', 'profile_picture')
    # ### end Alembic commands ###
