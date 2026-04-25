from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Library
from app.schemas.schemas import LibraryCreate, LibraryOut

router = APIRouter(prefix="/libraries", tags=["Libraries"])


@router.get("/", response_model=List[LibraryOut])
async def list_libraries(location_id: int | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Library)
    if location_id:
        q = q.where(Library.location_id == location_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=LibraryOut, status_code=201)
async def create_library(body: LibraryCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    lib = Library(**body.model_dump())
    db.add(lib)
    await db.commit()
    await db.refresh(lib)
    return lib


@router.get("/{library_id}", response_model=LibraryOut)
async def get_library(library_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    return lib


@router.put("/{library_id}", response_model=LibraryOut)
async def update_library(library_id: int, body: LibraryCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    for k, v in body.model_dump().items():
        setattr(lib, k, v)
    await db.commit()
    await db.refresh(lib)
    return lib


@router.delete("/{library_id}", status_code=204)
async def delete_library(library_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    lib = await db.get(Library, library_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    await db.delete(lib)
    await db.commit()
