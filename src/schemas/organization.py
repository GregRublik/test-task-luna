from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from schemas.building import BuildingResponse
from schemas.activity import ActivityResponse

class PaginationParams(BaseModel):
    limit: int = Field(
        50,
        ge=1,
        le=100,
        description="Количество элементов в ответе",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Смещение выборки",
    )


class OrganizationBase(BaseModel):
    name: str
    building_id: int
    phone_numbers: List[str] = Field(default_factory=list)


class OrganizationCreate(OrganizationBase):
    activity_ids: List[int] = []


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[str]] = None
    activity_ids: Optional[List[int]] = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    building_id: int
    phone_numbers: List[str]
    building: BuildingResponse
    activities: List[ActivityResponse]

    model_config = ConfigDict(from_attributes=True)


# Специальные схемы для запросов
class CoordinateRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Широта центра поиска"),
    longitude: float = Field(..., ge=-180, le=180, description="Долгота центра поиска"),


class RadiusSearchRequest(CoordinateRequest):
    radius_km: float = Field(gt=0, description="Радиус в километрах")


class OrganizationSearchRequest(BaseModel):
    name: Optional[str] = None
    activity_id: Optional[int] = None
    building_id: Optional[int] = None


class OrganizationFilter(BaseModel):
    building_id: int | None = None
    activity_id: int | None = None
    name: str | None = None

class OrganizationListParams(PaginationParams):
    building_id: int | None = Field(None, description="ID здания")
    activity_id: int | None = Field(None, description="ID деятельности")
    name: str | None = Field(None, description="Поиск по названию")

    include_subactivities: bool = Field(
        False,
        description="Искать по поддеятельностям",
    )

    def to_filter(self) -> OrganizationFilter:
        return OrganizationFilter(
            building_id=self.building_id,
            activity_id=self.activity_id,
            name=self.name,
        )

class RectangleSearchRequest(BaseModel):
    min_lat: float = Field(..., ge=-90, le=90,description="Широта первого угла прямоугольника")
    max_lat: float = Field(..., ge=-90, le=90, description="Широта второго угла прямоугольника")
    min_lon: float = Field(..., ge=-180, le=180, description="Долгота первого угла прямоугольника")
    max_lon: float = Field(..., ge=-180, le=180, description="Долгота второго угла прямоугольника")

    @model_validator(mode="after")
    def validate_rectangle(self):
        if self.min_lat > self.max_lat:
            raise ValueError("min_lat must be less than or equal to max_lat")

        if self.min_lon > self.max_lon:
            raise ValueError("min_lon must be less than or equal to max_lon")

        return self
