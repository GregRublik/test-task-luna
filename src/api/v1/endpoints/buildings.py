from fastapi import APIRouter, Depends, Query
from depends import verify_api_key
from schemas.building import BuildingResponse
from typing import List, Annotated
from services.building import BuildingService
from depends import get_building_service


router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@router.get("/buildings", response_model=List[BuildingResponse])
async def get_buildings(
    building_service: Annotated[BuildingService, Depends(get_building_service)], # noqa

    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[BuildingResponse]:
    """
    Возвращает список активностей для наглядности

    :return: List[BuildingResponse]
    """
    return await building_service.get_buildings(limit, offset)
