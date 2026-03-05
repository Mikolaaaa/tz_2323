from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Activity, Building, Organization, OrganizationPhone
from app.db.session import SessionLocal


# Keep dataset compact and realistic for a test assignment.
def seed_data(db: Session) -> None:
    existing = db.scalar(select(Organization.id).limit(1))
    if existing is not None:
        return

    b1 = Building(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6176)
    b2 = Building(address="г. Москва, ул. Блюхера 32/1", latitude=55.7512, longitude=37.6189)
    b3 = Building(address="г. Москва, пр. Мира 10", latitude=55.7801, longitude=37.6333)
    b4 = Building(address="г. Москва, ул. Тверская 5", latitude=55.7655, longitude=37.6051)
    db.add_all([b1, b2, b3, b4])

    food = Activity(name="Еда", level=1)
    meat = Activity(name="Мясная продукция", level=2, parent=food)
    dairy = Activity(name="Молочная продукция", level=2, parent=food)

    auto = Activity(name="Автомобили", level=1)
    trucks = Activity(name="Грузовые", level=2, parent=auto)
    cars = Activity(name="Легковые", level=2, parent=auto)
    spare_parts = Activity(name="Запчасти", level=3, parent=cars)
    accessories = Activity(name="Аксессуары", level=3, parent=cars)

    db.add_all([food, meat, dairy, auto, trucks, cars, spare_parts, accessories])
    db.flush()

    org1 = Organization(name='ООО "Рога и Копыта"', building=b2, activities=[meat, dairy])
    org1.phones = [
        OrganizationPhone(number="2-222-222"),
        OrganizationPhone(number="3-333-333"),
        OrganizationPhone(number="8-923-666-13-13"),
    ]

    org2 = Organization(name="ЕдаМаркет", building=b1, activities=[food])
    org2.phones = [OrganizationPhone(number="8-495-000-00-01")]

    org3 = Organization(name="ГрузТранс", building=b3, activities=[trucks])
    org3.phones = [OrganizationPhone(number="8-495-000-00-02")]

    org4 = Organization(name="АвтоМир Сервис", building=b4, activities=[spare_parts, accessories])
    org4.phones = [OrganizationPhone(number="8-495-000-00-03")]

    db.add_all([org1, org2, org3, org4])
    db.commit()


def run() -> None:
    with SessionLocal() as db:
        seed_data(db)


if __name__ == "__main__":
    run()
