from repositories.building import BuildingRepository
from services.unit_of_work import UnitOfWork
from typing import Optional, List
from schemas.building import BuildingResponse

class BuildingService:

    def __init__(
            self,
            repository: BuildingRepository,
            uow: UnitOfWork,
    ):
        self.repository = repository
        self.uow = uow

    async def get_buildings(self, limit: Optional[int] = 50, offset: Optional[int] = 0) -> List[BuildingResponse]:
        return await self.repository.find_all(self.uow.session,limit=limit, offset=offset)
