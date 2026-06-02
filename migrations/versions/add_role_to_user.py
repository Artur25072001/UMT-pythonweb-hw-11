"""add_role_to_user

Revision ID: add_role_to_user
Revises: 031be884c980
Create Date: 2026-06-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_role_to_user"
down_revision: Union[str, None] = "031be884c980"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(), server_default="user"))


def downgrade() -> None:
    op.drop_column("users", "role")
