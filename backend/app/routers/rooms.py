from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Room, RoomReservation
from app.schemas.schemas import (
    RoomCreate, RoomOut, RoomUpdate,
    RoomReservationCreate, RoomReservationOut, RoomReservationUpdate,
)

# ──────────────────────────────────────────
# ROOMS
# ──────────────────────────────────────────

rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@rooms_router.get("/", response_model=List[RoomOut])
async def list_rooms(library_id: int | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Room)
    if library_id:
        q = q.where(Room.library_id == library_id)
    return (await db.execute(q)).scalars().all()


@rooms_router.post("/", response_model=RoomOut, status_code=201)
async def create_room(body: RoomCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = Room(**body.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@rooms_router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(Room, room_id)
    if not r:
        raise HTTPException(404, "Room not found")
    return r


@rooms_router.patch("/{room_id}", response_model=RoomOut)
async def update_room(room_id: int, body: RoomUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(Room, room_id)
    if not r:
        raise HTTPException(404, "Room not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(r, k, v)
    await db.commit()
    await db.refresh(r)
    return r


@rooms_router.delete("/{room_id}", status_code=204)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(Room, room_id)
    if not r:
        raise HTTPException(404, "Room not found")
    await db.delete(r)
    await db.commit()


# ──────────────────────────────────────────
# ROOM RESERVATIONS
# ──────────────────────────────────────────

reservations_router = APIRouter(prefix="/reservations", tags=["Rooms"])


@reservations_router.get("/", response_model=List[RoomReservationOut])
async def list_reservations(
    room_id: int | None = None,
    patron_id: int | None = None,
    reservation_status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(RoomReservation)
    if room_id:
        q = q.where(RoomReservation.room_id == room_id)
    if patron_id:
        q = q.where(RoomReservation.patron_id == patron_id)
    if reservation_status:
        q = q.where(RoomReservation.reservation_status == reservation_status)
    return (await db.execute(q)).scalars().all()


@reservations_router.post("/", response_model=RoomReservationOut, status_code=201)
async def create_reservation(body: RoomReservationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    res = RoomReservation(**body.model_dump())
    db.add(res)
    await db.commit()
    await db.refresh(res)
    return res


@reservations_router.get("/{reservation_id}", response_model=RoomReservationOut)
async def get_reservation(reservation_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(RoomReservation, reservation_id)
    if not r:
        raise HTTPException(404, "Reservation not found")
    return r


@reservations_router.patch("/{reservation_id}", response_model=RoomReservationOut)
async def update_reservation_status(reservation_id: int, body: RoomReservationUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(RoomReservation, reservation_id)
    if not r:
        raise HTTPException(404, "Reservation not found")
    r.reservation_status = body.reservation_status
    await db.commit()
    await db.refresh(r)
    return r


@reservations_router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    r = await db.get(RoomReservation, reservation_id)
    if not r:
        raise HTTPException(404, "Reservation not found")
    await db.delete(r)
    await db.commit()
