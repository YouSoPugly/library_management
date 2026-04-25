from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import Staff
from app.schemas.schemas import StaffCreate, StaffOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=Token, summary="Login with email + password")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Standard OAuth2 password flow. Submit `username` (staff email) and
    `password` as form fields. Returns a Bearer JWT on success.
    """
    result = await db.execute(select(Staff).where(Staff.email == form_data.username))
    staff = result.scalar_one_or_none()

    if not staff or not verify_password(form_data.password, staff.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(staff.staff_id)})
    return Token(access_token=token)


@router.post("/register", response_model=StaffOut, status_code=status.HTTP_201_CREATED,
             summary="Register a new staff account")
async def register(
    body: StaffCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new staff member. In production, protect this endpoint or
    require an admin token — left open here for initial setup convenience.
    """
    existing = await db.execute(select(Staff).where(Staff.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    staff = Staff(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        hashed_password=hash_password(body.password),
        library_id=body.library_id,
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return staff


@router.get("/me", response_model=StaffOut, summary="Current authenticated staff")
async def me(current: Staff = Depends(get_current_staff)):
    return current
