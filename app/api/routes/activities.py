import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.models import Activity
from app.db.session import get_db
from app.schemas.activity import ActivityRead

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[ActivityRead], summary="Список деятельностей")
def list_activities(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Activity]:
    stmt = select(Activity).order_by(Activity.level, Activity.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/{activity_id}", response_model=ActivityRead, summary="Деятельность по ID")
def get_activity(activity_id: uuid.UUID, db: Session = Depends(get_db)) -> Activity:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity
