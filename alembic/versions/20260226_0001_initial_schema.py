"""initial schema

Revision ID: 20260226_0001
Revises:
Create Date: 2026-02-26 10:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260226_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("address"),
    )
    op.create_index(op.f("ix_buildings_address"), "buildings", ["address"], unique=False)

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "(parent_id IS NULL AND level = 1) OR (parent_id IS NOT NULL AND level > 1)",
            name="ck_activity_parent_level",
        ),
        sa.CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level_range"),
        sa.ForeignKeyConstraint(["parent_id"], ["activities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "parent_id", name="uq_activity_name_parent"),
    )
    op.create_index(op.f("ix_activities_name"), "activities", ["name"], unique=False)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organizations_building_id"), "organizations", ["building_id"], unique=False)
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)

    op.create_table(
        "organization_activity",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )

    op.create_table(
        "organization_phones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("number", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organization_phones_organization_id"), "organization_phones", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_organization_phones_organization_id"), table_name="organization_phones")
    op.drop_table("organization_phones")
    op.drop_table("organization_activity")

    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_building_id"), table_name="organizations")
    op.drop_table("organizations")

    op.drop_index(op.f("ix_activities_name"), table_name="activities")
    op.drop_table("activities")

    op.drop_index(op.f("ix_buildings_address"), table_name="buildings")
    op.drop_table("buildings")
