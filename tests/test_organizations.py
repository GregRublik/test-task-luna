import sys
sys.path.append("src/")

import pytest
from httpx import AsyncClient
from schemas.organization import OrganizationResponse
from schemas.building import BuildingResponse
from schemas.activity import ActivityResponse
from exceptions import OrganizationNoFoundException



@pytest.mark.asyncio
async def test_get_organizations_success(client: AsyncClient, mock_org_service):
    mock_org_service.get_organizations.return_value = [
        OrganizationResponse(
            id=1,
            name="Org 1",
            building_id=1,
            phone_numbers=[],
            building=BuildingResponse(id=1, address="Addr 1", latitude=55.0, longitude=37.0),
            activities=[
                ActivityResponse(id=1, name="Activity 1", parent_id=None, level=0, children=[]),
                ActivityResponse(id=2, name="Activity 2", parent_id=None, level=0, children=[])
            ]
        ),
        OrganizationResponse(
            id=2,
            name="Org 2",
            building_id=1,
            phone_numbers=[],
            building=BuildingResponse(id=1, address="Addr 1", latitude=55.0, longitude=37.0),
            activities=[
                ActivityResponse(id=2, name="Activity 2", parent_id=None, level=0, children=[])
            ]
        ),
    ]

    response = await client.get("/api/v1/organizations?building_id=1&limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Org 1"
    mock_org_service.get_organizations.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_organization_success(client: AsyncClient, mock_org_service):
    mock_org_service.get_organization.return_value = OrganizationResponse(
        id=1,
        name="Org 1",
        building_id=1,
        phone_numbers=[],
        building=BuildingResponse(id=1, address="Addr 1", latitude=55.0, longitude=37.0),
        activities=[
            ActivityResponse(id=2, name="Activity 2", parent_id=None, level=0, children=[])
        ]
    )

    response = await client.get("/api/v1/organizations/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Org 1"
    mock_org_service.get_organization.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_organization_not_found(client: AsyncClient, mock_org_service):
    mock_org_service.get_organization.side_effect = OrganizationNoFoundException()

    response = await client.get("/api/v1/organizations/999")
    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"
    mock_org_service.get_organization.assert_awaited_once_with(999)


@pytest.mark.asyncio
async def test_get_organizations_within_radius(client: AsyncClient, mock_org_service):
    mock_org_service.get_organizations_within_radius.return_value = []

    response = await client.get(
        "/api/v1/organizations/within_radius?latitude=55.75&longitude=37.62&radius_km=10"
    )
    assert response.status_code == 200
    assert response.json() == []
    mock_org_service.get_organizations_within_radius.assert_awaited_once_with(55.75, 37.62, 10)


@pytest.mark.asyncio
async def test_get_organizations_within_rectangle(client: AsyncClient, mock_org_service):
    mock_org_service.get_organizations_within_rectangle.return_value = []

    response = await client.get(
        "/api/v1/organizations/within_rectangle?min_lat=55.0&max_lat=56.0&min_lon=37.0&max_lon=38.0"
    )
    assert response.status_code == 200
    assert response.json() == []
    mock_org_service.get_organizations_within_rectangle.assert_awaited_once_with(55.0, 56.0, 37.0, 38.0)


@pytest.mark.asyncio
async def test_get_organizations_with_filters(client: AsyncClient, mock_org_service):
    mock_org_service.get_organizations.return_value = [
        OrganizationResponse(
            id=1,
            name="Filtered Org",
            building_id=2,
            phone_numbers=[],
            building=BuildingResponse(id=2, address="Addr 2", latitude=55.5, longitude=37.5),
            activities=[
                ActivityResponse(id=2, name="Activity 2", parent_id=None, level=0, children=[])
            ]
        )
    ]

    response = await client.get(
        "/api/v1/organizations?building_id=2&activity_id=3&name=Filtered"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Filtered Org"
    mock_org_service.get_organizations.assert_awaited_once()


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, mock_org_service):
    mock_org_service.get_organizations.return_value = [
        OrganizationResponse(
            id=i,
            name=f"Org {i}",
            building_id=1,
            phone_numbers=[],
            building=BuildingResponse(id=1, address="Addr 1", latitude=55.0, longitude=37.0),
            activities=[
                ActivityResponse(id=2, name="Activity 2", parent_id=None, level=0, children=[])
            ]
        ) for i in range(1, 6)
    ]

    response = await client.get("/api/v1/organizations?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    mock_org_service.get_organizations.assert_awaited_once()
