from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)

    organizations: Mapped[list[Organization]] = relationship(back_populates="building")


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        UniqueConstraint("name", "parent_id", name="uq_activity_name_parent"),
        CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level_range"),
        CheckConstraint(
            "(parent_id IS NULL AND level = 1) OR (parent_id IS NOT NULL AND level > 1)",
            name="ck_activity_parent_level",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    level: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    parent: Mapped[Activity | None] = relationship(remote_side="Activity.id", back_populates="children")
    children: Mapped[list[Activity]] = relationship(back_populates="parent")
    organizations: Mapped[list[Organization]] = relationship(
        secondary=organization_activity,
        back_populates="activities",
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True)
    building_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("buildings.id", ondelete="RESTRICT"),
        index=True,
    )

    building: Mapped[Building] = relationship(back_populates="organizations")
    phones: Mapped[list[OrganizationPhone]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list[Activity]] = relationship(
        secondary=organization_activity,
        back_populates="organizations",
    )


class OrganizationPhone(Base):
    __tablename__ = "organization_phones"
    __table_args__ = (UniqueConstraint("organization_id", "number", name="uq_org_phone_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    number: Mapped[str] = mapped_column(String(50))

    organization: Mapped[Organization] = relationship(back_populates="phones")
