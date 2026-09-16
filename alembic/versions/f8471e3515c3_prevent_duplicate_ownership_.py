"""prevent duplicate ownership relationships

Revision ID: f8471e3515c3
Revises: cf5496d8475e
Create Date: 2026-09-17 01:27:05.182754

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f8471e3515c3"
down_revision: Union[str, Sequence[str], None] = "cf5496d8475e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_ownership_history_unit_owner",
        "ownership_history",
        ["unit_id", "owner_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_ownership_history_unit_owner",
        "ownership_history",
        type_="unique",
    )