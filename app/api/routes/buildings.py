import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.models import Building
from app.db.session import get_db
from app.schemas.building import BuildingRead

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[BuildingRead], summary="Список зданий")
def list_buildings(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Building]:
    stmt = select(Building).order_by(Building.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/{building_id}", response_model=BuildingRead, summary="Здание по ID")
def get_building(building_id: uuid.UUID, db: Session = Depends(get_db)) -> Building:
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    return building
