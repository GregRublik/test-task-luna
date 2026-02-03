from db.models import Building
from repositories.base import SQLAlchemyRepository


class BuildingRepository(SQLAlchemyRepository):
    model = Building
