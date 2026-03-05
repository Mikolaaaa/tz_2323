"""add performance indexes and phone uniqueness

Revision ID: 20260305_0002
Revises: 20260226_0001
Create Date: 2026-03-05 16:00:00
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260305_0002"
down_revision: Union[str, Sequence[str], None] = "20260226_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_buildings_latitude"), "buildings", ["latitude"], unique=False)
    op.create_index(op.f("ix_buildings_longitude"), "buildings", ["longitude"], unique=False)
    op.create_index(op.f("ix_activities_parent_id"), "activities", ["parent_id"], unique=False)
    op.create_unique_constraint("uq_org_phone_number", "organization_phones", ["organization_id", "number"])


def downgrade() -> None:
    op.drop_constraint("uq_org_phone_number", "organization_phones", type_="unique")
    op.drop_index(op.f("ix_activities_parent_id"), table_name="activities")
    op.drop_index(op.f("ix_buildings_longitude"), table_name="buildings")
    op.drop_index(op.f("ix_buildings_latitude"), table_name="buildings")
