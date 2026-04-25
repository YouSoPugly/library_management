from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import Staff

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_staff(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Staff:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    staff_id: int = payload.get("sub")
    if staff_id is None:
        raise credentials_exception

    result = await db.execute(select(Staff).where(Staff.staff_id == int(staff_id)))
    staff = result.scalar_one_or_none()
    if staff is None:
        raise credentials_exception
    return staff
