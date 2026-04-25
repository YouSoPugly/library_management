from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import University
from app.schemas.schemas import UniversityCreate, UniversityOut

router = APIRouter(prefix="/universities", tags=["Universities"])


@router.get("/", response_model=List[UniversityOut])
async def list_universities(db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    result = await db.execute(select(University))
    return result.scalars().all()


@router.post("/", response_model=UniversityOut, status_code=201)
async def create_university(body: UniversityCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    uni = University(**body.model_dump())
    db.add(uni)
    await db.commit()
    await db.refresh(uni)
    return uni


@router.get("/{university_id}", response_model=UniversityOut)
async def get_university(university_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    uni = await db.get(University, university_id)
    if not uni:
        raise HTTPException(404, "University not found")
    return uni


@router.put("/{university_id}", response_model=UniversityOut)
async def update_university(university_id: int, body: UniversityCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    uni = await db.get(University, university_id)
    if not uni:
        raise HTTPException(404, "University not found")
    uni.name = body.name
    await db.commit()
    await db.refresh(uni)
    return uni


@router.delete("/{university_id}", status_code=204)
async def delete_university(university_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    uni = await db.get(University, university_id)
    if not uni:
        raise HTTPException(404, "University not found")
    await db.delete(uni)
    await db.commit()
