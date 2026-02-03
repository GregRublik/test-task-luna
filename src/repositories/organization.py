from sqlalchemy.exc import NoResultFound

from exceptions import ModelNoFoundException
from repositories.base import SQLAlchemyRepository
from sqlalchemy.orm import relationship, joinedload, selectinload
from sqlalchemy import select, func
from db.models import Organization, Activity, Building
from sqlalchemy.ext.asyncio import AsyncSession


class OrganizationRepository(SQLAlchemyRepository):
    model = Organization

    # ---------- ОБЩИЙ eager load ----------
    def _base_stmt(self):
        return (
            select(self.model)
            .join(self.model.building)
            .options(
                selectinload(self.model.building),
                selectinload(self.model.activities)
                .selectinload(Activity.children),
            )
        )

    # ---------- В РАДИУСЕ ----------
    async def find_within_radius(
            self,
            session: AsyncSession,
            latitude: float,
            longitude: float,
            radius_km: float,
    ):
        earth_radius = 6371  # км

        distance_expr = (
                earth_radius
                * func.acos(
            func.cos(func.radians(latitude))
            * func.cos(func.radians(Building.latitude))
            * func.cos(func.radians(Building.longitude) - func.radians(longitude))
            + func.sin(func.radians(latitude))
            * func.sin(func.radians(Building.latitude))
        )
        )

        stmt = (
            self._base_stmt()
            .where(distance_expr <= radius_km)
        )

        res = await session.execute(stmt)
        return res.scalars().unique().all()

    # ---------- В ПРЯМОУГОЛЬНИКЕ ----------
    async def find_within_rectangle(
            self,
            session: AsyncSession,
            min_lat: float,
            max_lat: float,
            min_lon: float,
            max_lon: float,
    ):
        stmt = (
            self._base_stmt()
            .where(
                Building.latitude.between(min_lat, max_lat),
                Building.longitude.between(min_lon, max_lon),
            )
        )

        res = await session.execute(stmt)
        return res.scalars().unique().all()


    async def find_by_activity_ids(
            self,
            session: AsyncSession,
            activity_ids: list[int],
            limit: int = 50,
            offset: int = 0,
    ):
        stmt = (
            select(self.model)
            .join(self.model.activities)
            .where(Activity.id.in_(activity_ids))
            .limit(limit).offset(offset)
            .options(
                selectinload(self.model.building),
                selectinload(self.model.activities)
                .selectinload(Activity.children),
            )
        )

        res = await session.execute(stmt)
        return res.scalars().unique().all()

    async def find_all(
            self,
            session: AsyncSession,
            filters: dict | None = None,
            limit: int = 50,
            offset: int = 0,
    ):
        stmt = (
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.activities)
                .selectinload(Activity.children),
            ).limit(limit).offset(offset)
        )

        if filters:
            conditions = []

            # обычные фильтры по полям Organization
            if "building_id" in filters:
                conditions.append(Organization.building_id == filters["building_id"])

            if "name" in filters:
                conditions.append(Organization.name.ilike(f"%{filters['name']}%"))

            # ⚠️ activity_id — через JOIN
            if "activity_id" in filters:
                stmt = stmt.join(Organization.activities).where(
                    Activity.id == filters["activity_id"]
                )

            if conditions:
                stmt = stmt.where(*conditions)

        res = await session.execute(stmt)
        return res.scalars().unique().all()

    async def get_by_id(
            self,
            session: AsyncSession,
            obj_id: int,
    ):
        stmt = (
            select(Organization)
            .where(Organization.id == obj_id)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.activities)
                .selectinload(Activity.children),
            )
        )

        try:
            res = await session.execute(stmt)
            return res.scalar_one()

        except NoResultFound:
            raise ModelNoFoundException
