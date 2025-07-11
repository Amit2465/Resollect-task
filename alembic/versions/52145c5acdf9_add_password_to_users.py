"""add password to users

Revision ID: 52145c5acdf9
Revises: c8c84c82c240
Create Date: 2025-07-11 10:29:07.864599
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '52145c5acdf9'
down_revision: Union[str, Sequence[str], None] = 'c8c84c82c240'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password column to users table."""
    op.add_column('users', sa.Column('password', sa.String(length=128), nullable=False))


def downgrade() -> None:
    """Remove password column from users table."""
    op.drop_column('users', 'password')
