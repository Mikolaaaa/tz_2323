import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, aliased, selectinload

from app.core.security import require_api_key
from app.db.models import Activity, Building, Organization, organization_activity
from app.db.session import get_db
from app.schemas.organization import OrganizationRead

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(require_api_key)],
)


def base_org_stmt():
    return select(Organization).options(
        selectinload(Organization.building),
        selectinload(Organization.phones),
        selectinload(Organization.activities),
    )


def with_pagination(stmt, limit: int, offset: int):
    return stmt.limit(limit).offset(offset)


def get_existing_activity(db: Session, activity_id: uuid.UUID) -> Activity:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


def get_existing_building(db: Session, building_id: uuid.UUID) -> Building:
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    return building


@router.get("/by-building/{building_id}", response_model=list[OrganizationRead], summary="Организации в здании")
def organizations_by_building(
    building_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    get_existing_building(db, building_id)
    stmt = with_pagination(
        base_org_stmt().where(Organization.building_id == building_id).order_by(Organization.id),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get("/by-activity/{activity_id}", response_model=list[OrganizationRead], summary="Организации по точной деятельности")
def organizations_by_activity(
    activity_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    get_existing_activity(db, activity_id)
    stmt = with_pagination(
        (
            base_org_stmt()
            .join(organization_activity, Organization.id == organization_activity.c.organization_id)
            .where(organization_activity.c.activity_id == activity_id)
            .distinct()
            .order_by(Organization.id)
        ),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get(
    "/by-activity-tree/{activity_id}",
    response_model=list[OrganizationRead],
    summary="Организации по деятельности и вложенным узлам",
)
def organizations_by_activity_tree(
    activity_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    get_existing_activity(db, activity_id)

    activity_tree = select(Activity.id).where(Activity.id == activity_id).cte(name="activity_tree", recursive=True)
    activity_alias = aliased(Activity)
    activity_tree = activity_tree.union_all(
        select(activity_alias.id).where(activity_alias.parent_id == activity_tree.c.id)
    )

    stmt = with_pagination(
        (
            base_org_stmt()
            .join(organization_activity, Organization.id == organization_activity.c.organization_id)
            .where(organization_activity.c.activity_id.in_(select(activity_tree.c.id)))
            .distinct()
            .order_by(Organization.id)
        ),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get("/geo/radius", response_model=list[OrganizationRead], summary="Организации в радиусе")
def organizations_in_radius(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0, le=20000),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    lat_rad = func.radians(latitude)
    lon_rad = func.radians(longitude)

    cos_arg = (
        func.cos(lat_rad)
        * func.cos(func.radians(Building.latitude))
        * func.cos(func.radians(Building.longitude) - lon_rad)
        + func.sin(lat_rad) * func.sin(func.radians(Building.latitude))
    )
    clamped_cos_arg = func.least(1.0, func.greatest(-1.0, cos_arg))
    distance_km = 6371.0 * func.acos(clamped_cos_arg)

    stmt = with_pagination(
        (
            base_org_stmt()
            .join(Building, Organization.building_id == Building.id)
            .where(distance_km <= radius_km)
            .distinct()
            .order_by(Organization.id)
        ),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get("/geo/box", response_model=list[OrganizationRead], summary="Организации в прямоугольной области")
def organizations_in_box(
    min_lat: float = Query(..., ge=-90, le=90),
    max_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lon: float = Query(..., ge=-180, le=180),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    if min_lat > max_lat or min_lon > max_lon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bounding box")

    stmt = with_pagination(
        (
            base_org_stmt()
            .join(Building, Organization.building_id == Building.id)
            .where(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon,
                )
            )
            .distinct()
            .order_by(Organization.id)
        ),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get("/search", response_model=list[OrganizationRead], summary="Поиск организаций по названию")
def search_organizations(
    q: str = Query(..., min_length=1, description="Часть названия организации"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Organization]:
    stmt = with_pagination(
        (
            base_org_stmt()
            .where(Organization.name.ilike(f"%{q}%"))
            .order_by(Organization.id)
        ),
        limit=limit,
        offset=offset,
    )
    return db.scalars(stmt).all()


@router.get("/{organization_id}", response_model=OrganizationRead, summary="Карточка организации по ID")
def organization_by_id(organization_id: uuid.UUID, db: Session = Depends(get_db)) -> Organization:
    stmt = base_org_stmt().where(Organization.id == organization_id)
    organization = db.scalar(stmt)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization
