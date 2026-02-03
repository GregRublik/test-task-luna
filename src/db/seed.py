import asyncio
from sqlalchemy import select

from db.database import async_session_maker
from db.models import Building, Activity, Organization


async def seed_db():
    async with async_session_maker() as session:

        # --- защита от повторного заполнения ---
        result = await session.execute(select(Organization).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded")
            return

        print("Seeding database...")

        # =========================
        # Activities (3 уровня)
        # =========================

        # Уровень 1
        food = Activity(name="Еда", level=1)
        auto = Activity(name="Автомобили", level=1)

        session.add_all([food, auto])
        await session.flush()

        # Уровень 2
        meat = Activity(name="Мясная продукция", level=2, parent_id=food.id)
        milk = Activity(name="Молочная продукция", level=2, parent_id=food.id)

        cargo = Activity(name="Грузовые", level=2, parent_id=auto.id)
        passenger = Activity(name="Легковые", level=2, parent_id=auto.id)

        session.add_all([meat, milk, cargo, passenger])
        await session.flush()

        # Уровень 3
        parts = Activity(name="Запчасти", level=3, parent_id=passenger.id)
        accessories = Activity(name="Аксессуары", level=3, parent_id=passenger.id)

        session.add_all([parts, accessories])
        await session.flush()

        # =========================
        # Buildings
        # =========================

        building_1 = Building(
            address="г. Москва, ул. Ленина 1, офис 3",
            latitude=55.7558,
            longitude=37.6173,
        )

        building_2 = Building(
            address="г. Москва, ул. Блюхера 32/1",
            latitude=55.7510,
            longitude=37.6200,
        )

        session.add_all([building_1, building_2])
        await session.flush()

        # =========================
        # Organizations
        # =========================

        org_1 = Organization(
            name="ООО Рога и Копыта",
            building_id=building_1.id,
            phone_numbers=[
                "2-222-222",
                "3-333-333",
                "8-923-666-13-13",
            ],
            activities=[meat, milk],
        )

        org_2 = Organization(
            name="Мясной Дом",
            building_id=building_2.id,
            phone_numbers=["8-900-111-22-33"],
            activities=[meat],
        )

        org_3 = Organization(
            name="АвтоМир",
            building_id=building_2.id,
            phone_numbers=["8-495-123-45-67"],
            activities=[passenger, parts, accessories],
        )

        session.add_all([org_1, org_2, org_3])

        await session.commit()
        print("Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_db())
