from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Location
from app.schemas.schemas import LocationCreate, LocationOut

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/", response_model=List[LocationOut])
async def list_locations(university_id: int | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Location)
    if university_id:
        q = q.where(Location.university_id == university_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=LocationOut, status_code=201)
async def create_location(body: LocationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loc = Location(**body.model_dump())
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


@router.get("/{location_id}", response_model=LocationOut)
async def get_location(location_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loc = await db.get(Location, location_id)
    if not loc:
        raise HTTPException(404, "Location not found")
    return loc


@router.put("/{location_id}", response_model=LocationOut)
async def update_location(location_id: int, body: LocationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loc = await db.get(Location, location_id)
    if not loc:
        raise HTTPException(404, "Location not found")
    for k, v in body.model_dump().items():
        setattr(loc, k, v)
    await db.commit()
    await db.refresh(loc)
    return loc


@router.delete("/{location_id}", status_code=204)
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loc = await db.get(Location, location_id)
    if not loc:
        raise HTTPException(404, "Location not found")
    await db.delete(loc)
    await db.commit()
