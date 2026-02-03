from fastapi import FastAPI, Depends
from api.v1.endpoints import organizations, activities, buildings
from config import settings
import uvicorn
from exception_handlers import (
    model_not_found_handler,
    model_already_exists_handler,
    organization_not_found_handler,
)
from exceptions import ModelNoFoundException, ModelAlreadyExistsException, OrganizationNoFoundException

app = FastAPI()

app.add_exception_handler(
    ModelNoFoundException,
    model_not_found_handler,
)

app.add_exception_handler(
    ModelAlreadyExistsException,
    model_already_exists_handler,
)

app.add_exception_handler(
    OrganizationNoFoundException,
    organization_not_found_handler,
)

app.include_router(activities.router, prefix="/api/v1", tags=["activities"])
app.include_router(buildings.router, prefix="/api/v1", tags=["buildings"])
app.include_router(organizations.router, prefix="/api/v1", tags=["organizations"])



if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
