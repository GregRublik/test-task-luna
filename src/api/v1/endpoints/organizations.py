from fastapi import APIRouter, Depends, Query
from typing import List, Annotated
from services.organization import OrganizationService
from depends import get_organization_service, verify_api_key
from schemas.organization import (
    OrganizationResponse,
    RectangleSearchRequest,
    OrganizationListParams
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

        latitude: float = Query(..., ge=-90, le=90, description="Широта центра поиска"),
        longitude: float = Query(..., ge=-180, le=180, description="Долгота центра поиска"),
        radius_km: float = Query(..., gt=0, description="Радиус в километрах"),

):
    """
    Поиск в указанном радиусе поиска

    :param latitude:

    :param longitude:

    :param radius_km:

    :return:
    """
    return await organization_service.get_organizations_within_radius(
        latitude,
        longitude,
        radius_km
    )



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

    return await organization_service.get_organizations_within_rectangle(
        rectangle.min_lat,
        rectangle.max_lat,
        rectangle.min_lon,
        rectangle.max_lon
    )



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
