from typing import List

from db.models import Organization
from exceptions import OrganizationNoFoundException, ModelNoFoundException
from repositories.organization import OrganizationRepository
from repositories.activity import ActivityRepository
from services.unit_of_work import UnitOfWork

from schemas.organization import OrganizationFilter


class OrganizationService:

    def __init__(
            self,
            repository: OrganizationRepository,
            activity_repository: ActivityRepository,
            uow: UnitOfWork,
    ):
        self.repository = repository
        self.activity_repository = activity_repository
        self.uow = uow

    async def get_organizations(
            self,
            filters: OrganizationFilter,
            include_subactivities=False,
            limit: int = 50,
            offset: int = 0
    ) -> List[Organization]:

        # обычный поиск
        if not include_subactivities or filters.activity_id is None:
            return await self.repository.find_all(
                self.uow.session,
                filters.model_dump(exclude_none=True),
                limit,
                offset
            )

        # Поиск со связями
        activity_id = filters.activity_id
        activity_ids = await self.activity_repository.get_activity_subtree_ids(
            self.uow.session,
            activity_id,
        )
        return await self.repository.find_by_activity_ids(
            self.uow.session,
            activity_ids,
            limit,
            offset
        )

    async def get_organization(self, organization_id: int) -> Organization:
        try:
            return await self.repository.get_by_id(self.uow.session, organization_id)
        except ModelNoFoundException:
            raise OrganizationNoFoundException



    async def create_organization(self, organization_data: dict) -> Organization:
        async with self.uow:
            activity_ids = organization_data.pop("activity_ids")

            org = await self.repository.add_one(
                self.uow.session,
                organization_data
            )

            return org

    async def update_organization(self, organization_data: dict) -> Organization:
        async with self.uow:
            org = await self.repository.change_one(
                self.uow.session,
                organization_data
            )
            return org

    async def get_organizations_within_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ):
        return await self.repository.find_within_radius(
            self.uow.session,
            latitude,
            longitude,
            radius_km,
        )

    async def get_organizations_within_rectangle(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ):
        return await self.repository.find_within_rectangle(
            self.uow.session,
            min_lat,
            max_lat,
            min_lon,
            max_lon,
        )
