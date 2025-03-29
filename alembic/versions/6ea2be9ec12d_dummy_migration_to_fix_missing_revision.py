"""Dummy migration to fix missing revision

Revision ID: 6ea2be9ec12d
Revises: 
Create Date: 2025-03-29 18:21:11.552640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ea2be9ec12d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
