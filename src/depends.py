from repositories.activity import ActivityRepository
from repositories.building import BuildingRepository
from services import organization, unit_of_work, activity, building
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db_session
from repositories.organization import OrganizationRepository
from fastapi import security
from fastapi.security import HTTPBearer

from config import settings


def get_uow(
    session: AsyncSession = Depends(get_db_session),
) -> unit_of_work.UnitOfWork:
    return unit_of_work.UnitOfWork(session)


def verify_api_key(credentials: security.HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> bool:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    try:
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")

        if credentials.credentials != settings.api_key:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

        return True
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")



def get_organization_repository() -> OrganizationRepository:
    return OrganizationRepository()

def get_activity_repository() -> ActivityRepository:
    return ActivityRepository()

def get_building_repository() -> BuildingRepository:
    return BuildingRepository()


def get_organization_service(
    repository: OrganizationRepository = Depends(get_organization_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    uow: unit_of_work.UnitOfWork = Depends(get_uow),
) -> organization.OrganizationService:
    return organization.OrganizationService(
        repository=repository,
        activity_repository=activity_repository,
        uow=uow,
    )

def get_activity_service(
        repository: ActivityRepository = Depends(get_activity_repository),
        uow: unit_of_work.UnitOfWork = Depends(get_uow),
) -> activity.ActivityService:
    return activity.ActivityService(
        repository=repository,
        uow=uow,
    )

def get_building_service(
        repository: BuildingRepository = Depends(get_building_repository),
        uow: unit_of_work.UnitOfWork = Depends(get_uow),
) -> building.BuildingService:
    return building.BuildingService(
        repository=repository,
        uow=uow,
    )
