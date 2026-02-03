from fastapi import APIRouter, Depends, Query
from depends import verify_api_key
from schemas.activity import ActivityResponse
from typing import List, Annotated
from services.activity import ActivityService
from depends import get_activity_service


router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@router.get("/activities", response_model=List[ActivityResponse])
async def get_activities(
    activity_service: Annotated[ActivityService, Depends(get_activity_service)], # noqa

    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ActivityResponse]:
    """
    Возвращает список активностей для наглядности

    :return: List[ActivityResponse]
    """
    return await activity_service.get_activities(limit, offset)
