from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: int
    level: int
    children: Optional[List['ActivityResponse']] = None

    model_config = ConfigDict(from_attributes=True)


# Рекурсивное обновление для ActivityResponse
ActivityResponse.model_rebuild()
