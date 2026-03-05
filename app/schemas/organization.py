import uuid

from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityRead
from app.schemas.building import BuildingRead


class OrganizationPhoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    building: BuildingRead
    phones: list[OrganizationPhoneRead]
    activities: list[ActivityRead]
