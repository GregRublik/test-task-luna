import sys

sys.path.append("src/")

import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from services.organization import OrganizationService
from repositories.organization import OrganizationRepository
from repositories.activity import ActivityRepository
from services import unit_of_work
from depends import (
    get_organization_service,
    get_uow,
    get_organization_repository,
    get_activity_repository,
    verify_api_key,
)


# Фикстура для мока UnitOfWork
@pytest.fixture
def mock_uow():
    mock = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    mock.organizations = AsyncMock()
    mock.activities = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


# Фикстура для мока репозитория
@pytest.fixture
def mock_org_repository():
    return AsyncMock(spec=OrganizationRepository)


# Фикстура для мока activity репозитория
@pytest.fixture
def mock_activity_repository():
    return AsyncMock(spec=ActivityRepository)


# Фикстура для мока OrganizationService
@pytest.fixture
def mock_org_service(mock_org_repository, mock_activity_repository, mock_uow):
    # Создаем mock сервиса
    service = AsyncMock(spec=OrganizationService)

    # Имитируем поведение конструктора
    service.repository = mock_org_repository
    service.activity_repository = mock_activity_repository
    service.uow = mock_uow

    return service


# Фикстура для подмены зависимостей
@pytest.fixture(autouse=True)
async def override_dependencies(mock_org_service):
    """Автоматически подменяем зависимости для всех тестов"""

    # Подменяем get_organization_service
    async def override_get_organization_service():
        return mock_org_service

    # Подменяем get_uow (возвращаем mock из сервиса)
    async def override_get_uow():
        return mock_org_service.uow

    # Подменяем get_organization_repository
    async def override_get_organization_repository():
        return mock_org_service.repository

    # Подменяем get_activity_repository
    async def override_get_activity_repository():
        return mock_org_service.activity_repository

    # Подменяем verify_api_key для пропуска аутентификации в тестах
    async def override_verify_api_key():
        return True

    app.dependency_overrides[get_organization_service] = override_get_organization_service
    app.dependency_overrides[get_uow] = override_get_uow
    app.dependency_overrides[get_organization_repository] = override_get_organization_repository
    app.dependency_overrides[get_activity_repository] = override_get_activity_repository
    app.dependency_overrides[verify_api_key] = override_verify_api_key

    yield

    # Очищаем после теста
    app.dependency_overrides.clear()


# Фикстура клиента
@pytest.fixture
async def client():
    """Асинхронный клиент для тестов"""
    async with AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
    ) as ac:
        yield ac


# Дополнительная фикстура для очистки
@pytest.fixture(autouse=True)
async def cleanup():
    """Очистка между тестами"""
    yield
    await asyncio.sleep(0.001)  # Небольшая пауза для завершения операций
