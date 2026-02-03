from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import ModelAlreadyExistsException, OrganizationNoFoundException, ModelNoFoundException

async def model_not_found_handler(
    request: Request,
    exc: ModelNoFoundException,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "not_found",
            "message": exc.detail,
        },
    )


async def model_already_exists_handler(
    request: Request,
    exc: ModelAlreadyExistsException,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "already_exists",
            "message": exc.detail,
        },
    )

async def organization_not_found_handler(
    request: Request,
    exc: OrganizationNoFoundException,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "organization_not_found",
            "message": exc.detail,
        },
    )
