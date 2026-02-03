from services.unit_of_work import UnitOfWork
from repositories.activity import ActivityRepository
from typing import List, Optional
from schemas.activity import ActivityResponse

class ActivityService:

    def __init__(
            self,
            repository: ActivityRepository,
            uow: UnitOfWork,
    ):
        self.repository = repository
        self.uow = uow

    async def get_activities(self, limit: Optional[int] = 50, offset: Optional[int] = 0) -> List[ActivityResponse]:
        return await self.repository.find_all(self.uow.session,limit=limit, offset=offset)
