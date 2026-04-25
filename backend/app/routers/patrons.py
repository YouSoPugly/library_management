from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Faculty, Patron, Student
from app.schemas.schemas import (
    FacultyCreate, FacultyOut,
    PatronCreate, PatronOut,
    StudentCreate, StudentOut,
)

# PATRONS

patrons_router = APIRouter(prefix="/patrons", tags=["Patrons"])


@patrons_router.get("/", response_model=List[PatronOut])
async def list_patrons(patron_type: str | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Patron)
    if patron_type:
        q = q.where(Patron.patron_type == patron_type)
    return (await db.execute(q)).scalars().all()


@patrons_router.post("/", response_model=PatronOut, status_code=201)
async def create_patron(body: PatronCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    existing = await db.execute(select(Patron).where(Patron.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Email already registered")
    patron = Patron(**body.model_dump())
    db.add(patron)
    await db.commit()
    await db.refresh(patron)
    return patron


@patrons_router.get("/{patron_id}", response_model=PatronOut)
async def get_patron(patron_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    p = await db.get(Patron, patron_id)
    if not p:
        raise HTTPException(404, "Patron not found")
    return p


@patrons_router.put("/{patron_id}", response_model=PatronOut)
async def update_patron(patron_id: int, body: PatronCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    p = await db.get(Patron, patron_id)
    if not p:
        raise HTTPException(404, "Patron not found")
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@patrons_router.delete("/{patron_id}", status_code=204)
async def delete_patron(patron_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    p = await db.get(Patron, patron_id)
    if not p:
        raise HTTPException(404, "Patron not found")
    await db.delete(p)
    await db.commit()


# STUDENTS

students_router = APIRouter(prefix="/students", tags=["Students"])


@students_router.get("/", response_model=List[StudentOut])
async def list_students(university_id: int | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Student)
    if university_id:
        q = q.where(Student.university_id == university_id)
    return (await db.execute(q)).scalars().all()


@students_router.post("/", response_model=StudentOut, status_code=201)
async def create_student(body: StudentCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    student = Student(**body.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@students_router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    s = await db.get(Student, student_id)
    if not s:
        raise HTTPException(404, "Student not found")
    return s


@students_router.put("/{student_id}", response_model=StudentOut)
async def update_student(student_id: int, body: StudentCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    s = await db.get(Student, student_id)
    if not s:
        raise HTTPException(404, "Student not found")
    for k, v in body.model_dump().items():
        setattr(s, k, v)
    await db.commit()
    await db.refresh(s)
    return s


@students_router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    s = await db.get(Student, student_id)
    if not s:
        raise HTTPException(404, "Student not found")
    await db.delete(s)
    await db.commit()


# FACULTY

faculty_router = APIRouter(prefix="/faculty", tags=["Faculty"])


@faculty_router.get("/", response_model=List[FacultyOut])
async def list_faculty(university_id: int | None = None, department: str | None = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    q = select(Faculty)
    if university_id:
        q = q.where(Faculty.university_id == university_id)
    if department:
        q = q.where(Faculty.department == department)
    return (await db.execute(q)).scalars().all()


@faculty_router.post("/", response_model=FacultyOut, status_code=201)
async def create_faculty(body: FacultyCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = Faculty(**body.model_dump())
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return f


@faculty_router.get("/{faculty_id}", response_model=FacultyOut)
async def get_faculty_member(faculty_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Faculty, faculty_id)
    if not f:
        raise HTTPException(404, "Faculty member not found")
    return f


@faculty_router.put("/{faculty_id}", response_model=FacultyOut)
async def update_faculty(faculty_id: int, body: FacultyCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Faculty, faculty_id)
    if not f:
        raise HTTPException(404, "Faculty member not found")
    for k, v in body.model_dump().items():
        setattr(f, k, v)
    await db.commit()
    await db.refresh(f)
    return f


@faculty_router.delete("/{faculty_id}", status_code=204)
async def delete_faculty(faculty_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Faculty, faculty_id)
    if not f:
        raise HTTPException(404, "Faculty member not found")
    await db.delete(f)
    await db.commit()
