"""add user profile image

Revision ID: ec805a7718eb
Revises: e12d86a9f8b9
Create Date: 2024-08-04 22:11:14.420081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec805a7718eb'
down_revision: Union[str, None] = 'e12d86a9f8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_image', sa.String(length=150), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'profile_image')
    # ### end Alembic commands ###
