from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.api.schemas.admin import (
    OrganizationCreate, OrganizationResponse,
    PersonCreate, PersonResponse,
    ContractCreate, ContractResponse,
)
from src.adapters.api.schemas.user import UserResponse
from src.adapters.db.models import Organization, Person, Contract, User
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_role

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ── Organizations CRUD ──

@router.get("/organizations", response_model=list[OrganizationResponse])
async def list_organizations(
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    result = await session.execute(
        select(Organization).order_by(Organization.name)
    )
    return result.scalars().all()


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    body: OrganizationCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    org = Organization(**body.model_dump())
    session.add(org)
    await session.flush()
    await session.refresh(org)
    return org


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID, body: OrganizationCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    org = await session.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(org, k, v)
    await session.flush()
    return org


@router.delete("/organizations/{org_id}", status_code=204)
async def delete_organization(
    org_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    org = await session.get(Organization, org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    org.is_active = False
    await session.flush()


# ── People CRUD ──

@router.get("/people", response_model=list[PersonResponse])
async def list_people(
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    result = await session.execute(select(Person).order_by(Person.full_name))
    return result.scalars().all()


@router.post("/people", response_model=PersonResponse, status_code=201)
async def create_person(
    body: PersonCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    person = Person(**body.model_dump())
    session.add(person)
    await session.flush()
    await session.refresh(person)
    return person


@router.patch("/people/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: UUID, body: PersonCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    person = await session.get(Person, person_id)
    if not person:
        raise HTTPException(404, "Person not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(person, k, v)
    await session.flush()
    return person


# ── Contracts CRUD ──

@router.get("/contracts", response_model=list[ContractResponse])
async def list_contracts(
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    result = await session.execute(select(Contract).order_by(Contract.subject))
    return result.scalars().all()


@router.post("/contracts", response_model=ContractResponse, status_code=201)
async def create_contract(
    body: ContractCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    contract = Contract(**body.model_dump())
    session.add(contract)
    await session.flush()
    await session.refresh(contract)
    return contract


@router.patch("/contracts/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: UUID, body: ContractCreate,
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    contract = await session.get(Contract, contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(contract, k, v)
    await session.flush()
    return contract


# ── Users list (admin only) ──

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    session: AsyncSession = Depends(get_async_session),
    _admin=Depends(require_role("admin")),
):
    result = await session.execute(select(User).order_by(User.name))
    return result.scalars().all()