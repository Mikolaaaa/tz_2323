import uuid

from pydantic import BaseModel, ConfigDict


class BuildingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    address: str
    latitude: float
    longitude: float
