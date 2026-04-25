from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.core.security import hash_password
from app.models.models import Permission, Role, RolePermission, Staff, StaffRole
from app.schemas.schemas import (
    PermissionCreate, PermissionOut,
    RoleCreate, RoleOut,
    RolePermissionCreate,
    StaffCreate, StaffOut,
    StaffRoleCreate,
)

# STAFF

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


@staff_router.get("/", response_model=List[StaffOut])
async def list_staff(library_id: int | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Staff)
    if library_id:
        q = q.where(Staff.library_id == library_id)
    return (await db.execute(q)).scalars().all()


@staff_router.post("/", response_model=StaffOut, status_code=201)
async def create_staff(body: StaffCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    existing = await db.execute(select(Staff).where(Staff.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Email already registered")
    data = body.model_dump()
    data["hashed_password"] = hash_password(data.pop("password"))
    s = Staff(**data)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@staff_router.get("/{staff_id}", response_model=StaffOut)
async def get_staff(staff_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    s = await db.get(Staff, staff_id)
    if not s:
        raise HTTPException(404, "Staff member not found")
    return s


@staff_router.delete("/{staff_id}", status_code=204)
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    s = await db.get(Staff, staff_id)
    if not s:
        raise HTTPException(404, "Staff member not found")
    await db.delete(s)
    await db.commit()


# ROLES

roles_router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@roles_router.get("/", response_model=List[RoleOut])
async def list_roles(db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    return (await db.execute(select(Role))).scalars().all()


@roles_router.post("/", response_model=RoleOut, status_code=201)
async def create_role(body: RoleCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = Role(**body.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@roles_router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(Role, role_id)
    if not r:
        raise HTTPException(404, "Role not found")
    await db.delete(r)
    await db.commit()


# PERMISSIONS

permissions_router = APIRouter(prefix="/permissions", tags=["Roles & Permissions"])


@permissions_router.get("/", response_model=List[PermissionOut])
async def list_permissions(db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    return (await db.execute(select(Permission))).scalars().all()


@permissions_router.post("/", response_model=PermissionOut, status_code=201)
async def create_permission(body: PermissionCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    p = Permission(**body.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@permissions_router.delete("/{permission_id}", status_code=204)
async def delete_permission(permission_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    p = await db.get(Permission, permission_id)
    if not p:
        raise HTTPException(404, "Permission not found")
    await db.delete(p)
    await db.commit()


# ROLE <-> PERMISSION  (many-to-many)

role_permissions_router = APIRouter(prefix="/role-permissions", tags=["Roles & Permissions"])


@role_permissions_router.post("/", status_code=201)
async def assign_permission_to_role(body: RolePermissionCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    rp = RolePermission(**body.model_dump())
    db.add(rp)
    await db.commit()
    return {"detail": "Permission assigned"}


@role_permissions_router.delete("/", status_code=204)
async def remove_permission_from_role(role_id: int, permission_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    rp = await db.get(RolePermission, (role_id, permission_id))
    if not rp:
        raise HTTPException(404, "Mapping not found")
    await db.delete(rp)
    await db.commit()


# STAFF <-> ROLE  (many-to-many)

staff_roles_router = APIRouter(prefix="/staff-roles", tags=["Roles & Permissions"])


@staff_roles_router.post("/", status_code=201)
async def assign_role_to_staff(body: StaffRoleCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    sr = StaffRole(**body.model_dump())
    db.add(sr)
    await db.commit()
    return {"detail": "Role assigned"}


@staff_roles_router.delete("/", status_code=204)
async def remove_role_from_staff(staff_id: int, role_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    sr = await db.get(StaffRole, (staff_id, role_id))
    if not sr:
        raise HTTPException(404, "Mapping not found")
    await db.delete(sr)
    await db.commit()
