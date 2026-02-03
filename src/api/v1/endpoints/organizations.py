from fastapi import APIRouter, Depends, Query
from typing import List, Annotated
from services.organization import OrganizationService
from depends import get_organization_service, verify_api_key
from schemas.organization import (
    OrganizationResponse,
    RectangleSearchRequest,
    OrganizationListParams, RadiusSearchRequest
)

router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)


@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_organizations(
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)], # noqa
    params: OrganizationListParams = Depends(),
):
    """
    Получить список организаций по фильтрам

    :param params: OrganizationListParams фильтры для поиска организации

    :return: List[OrganizationResponse]
    """

    return await organization_service.get_organizations(
        filters=params.to_filter(),
        include_subactivities=params.include_subactivities,
        limit=params.limit,
        offset=params.offset
    )


@router.get("/organizations/within_radius", response_model=List[OrganizationResponse])
async def get_organizations_within_radius(
        organization_service: Annotated[OrganizationService, Depends(get_organization_service)], # noqa
        params: RadiusSearchRequest = Depends(),
):
    """
    Поиск в указанном радиусе поиска

    :param params: RadiusSearchRequest координаты поиска и радиус от них

    :return:
    """
    return await organization_service.get_organizations_within_radius(params)



@router.get("/organizations/within_rectangle", response_model=List[OrganizationResponse])
async def get_organizations_within_rectangle(
        organization_service: Annotated[OrganizationService, Depends(get_organization_service)], # noqa
        rectangle: RectangleSearchRequest = Depends(),
):
    """
    Поиск организаций в указанной области

    :param rectangle: RectangleSearchRequest

    :return: List[OrganizationResponse]
    """

    return await organization_service.get_organizations_within_rectangle(rectangle)



@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
        organization_id: int,
        organization_service: Annotated[OrganizationService, Depends(get_organization_service)], # noqa
):
    """
    Получить организацию по id

    :param organization_id:

    :return: OrganizationResponse
    """
    return await organization_service.get_organization(organization_id)
