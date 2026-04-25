from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Checkout, Fine, Hold, InterLibraryLoan
from app.schemas.schemas import (
    CheckoutCreate, CheckoutOut, CheckoutReturn,
    FineCreate, FineOut, FineUpdate,
    HoldCreate, HoldOut, HoldUpdate,
    InterLibraryLoanCreate, InterLibraryLoanOut, InterLibraryLoanUpdate,
)

# ──────────────────────────────────────────
# CHECKOUTS
# ──────────────────────────────────────────

checkouts_router = APIRouter(prefix="/checkouts", tags=["Checkouts"])


@checkouts_router.get("/", response_model=List[CheckoutOut])
async def list_checkouts(
    patron_id: int | None = None,
    copy_id: int | None = None,
    overdue_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    from datetime import date
    q = select(Checkout)
    if patron_id:
        q = q.where(Checkout.patron_id == patron_id)
    if copy_id:
        q = q.where(Checkout.copy_id == copy_id)
    if overdue_only:
        q = q.where(Checkout.return_date.is_(None), Checkout.due_date < date.today())
    return (await db.execute(q)).scalars().all()


@checkouts_router.post("/", response_model=CheckoutOut, status_code=201)
async def create_checkout(body: CheckoutCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = Checkout(**body.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@checkouts_router.get("/{checkout_id}", response_model=CheckoutOut)
async def get_checkout(checkout_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(Checkout, checkout_id)
    if not c:
        raise HTTPException(404, "Checkout not found")
    return c


@checkouts_router.patch("/{checkout_id}/return", response_model=CheckoutOut,
                         summary="Record a return date")
async def return_item(checkout_id: int, body: CheckoutReturn, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(Checkout, checkout_id)
    if not c:
        raise HTTPException(404, "Checkout not found")
    if c.return_date:
        raise HTTPException(400, "Item already returned")
    c.return_date = body.return_date
    await db.commit()
    await db.refresh(c)
    return c


@checkouts_router.delete("/{checkout_id}", status_code=204)
async def delete_checkout(checkout_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(Checkout, checkout_id)
    if not c:
        raise HTTPException(404, "Checkout not found")
    await db.delete(c)
    await db.commit()


# ──────────────────────────────────────────
# HOLDS
# ──────────────────────────────────────────

holds_router = APIRouter(prefix="/holds", tags=["Holds"])


@holds_router.get("/", response_model=List[HoldOut])
async def list_holds(
    patron_id: int | None = None,
    item_id: int | None = None,
    hold_status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(Hold)
    if patron_id:
        q = q.where(Hold.patron_id == patron_id)
    if item_id:
        q = q.where(Hold.item_id == item_id)
    if hold_status:
        q = q.where(Hold.hold_status == hold_status)
    return (await db.execute(q)).scalars().all()


@holds_router.post("/", response_model=HoldOut, status_code=201)
async def create_hold(body: HoldCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    h = Hold(**body.model_dump())
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return h


@holds_router.get("/{hold_id}", response_model=HoldOut)
async def get_hold(hold_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    h = await db.get(Hold, hold_id)
    if not h:
        raise HTTPException(404, "Hold not found")
    return h


@holds_router.patch("/{hold_id}", response_model=HoldOut)
async def update_hold_status(hold_id: int, body: HoldUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    h = await db.get(Hold, hold_id)
    if not h:
        raise HTTPException(404, "Hold not found")
    h.hold_status = body.hold_status
    await db.commit()
    await db.refresh(h)
    return h


@holds_router.delete("/{hold_id}", status_code=204)
async def delete_hold(hold_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    h = await db.get(Hold, hold_id)
    if not h:
        raise HTTPException(404, "Hold not found")
    await db.delete(h)
    await db.commit()


# ──────────────────────────────────────────
# INTER-LIBRARY LOANS
# ──────────────────────────────────────────

ill_router = APIRouter(prefix="/inter-library-loans", tags=["Inter-Library Loans"])


@ill_router.get("/", response_model=List[InterLibraryLoanOut])
async def list_loans(
    source_library_id: int | None = None,
    destination_library_id: int | None = None,
    loan_status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(InterLibraryLoan)
    if source_library_id:
        q = q.where(InterLibraryLoan.source_library_id == source_library_id)
    if destination_library_id:
        q = q.where(InterLibraryLoan.destination_library_id == destination_library_id)
    if loan_status:
        q = q.where(InterLibraryLoan.loan_status == loan_status)
    return (await db.execute(q)).scalars().all()


@ill_router.post("/", response_model=InterLibraryLoanOut, status_code=201)
async def create_loan(body: InterLibraryLoanCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loan = InterLibraryLoan(**body.model_dump())
    db.add(loan)
    await db.commit()
    await db.refresh(loan)
    return loan


@ill_router.get("/{loan_id}", response_model=InterLibraryLoanOut)
async def get_loan(loan_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loan = await db.get(InterLibraryLoan, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found")
    return loan


@ill_router.patch("/{loan_id}", response_model=InterLibraryLoanOut)
async def update_loan(loan_id: int, body: InterLibraryLoanUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loan = await db.get(InterLibraryLoan, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(loan, k, v)
    await db.commit()
    await db.refresh(loan)
    return loan


@ill_router.delete("/{loan_id}", status_code=204)
async def delete_loan(loan_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    loan = await db.get(InterLibraryLoan, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found")
    await db.delete(loan)
    await db.commit()


# ──────────────────────────────────────────
# FINES
# ──────────────────────────────────────────

fines_router = APIRouter(prefix="/fines", tags=["Fines"])


@fines_router.get("/", response_model=List[FineOut])
async def list_fines(
    patron_id: int | None = None,
    paid_status: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(Fine)
    if patron_id:
        q = q.where(Fine.patron_id == patron_id)
    if paid_status is not None:
        q = q.where(Fine.paid_status == paid_status)
    return (await db.execute(q)).scalars().all()


@fines_router.post("/", response_model=FineOut, status_code=201)
async def create_fine(body: FineCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = Fine(**body.model_dump())
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return f


@fines_router.get("/{fine_id}", response_model=FineOut)
async def get_fine(fine_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Fine, fine_id)
    if not f:
        raise HTTPException(404, "Fine not found")
    return f


@fines_router.patch("/{fine_id}", response_model=FineOut, summary="Mark fine as paid/unpaid")
async def update_fine(fine_id: int, body: FineUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Fine, fine_id)
    if not f:
        raise HTTPException(404, "Fine not found")
    f.paid_status = body.paid_status
    await db.commit()
    await db.refresh(f)
    return f


@fines_router.delete("/{fine_id}", status_code=204)
async def delete_fine(fine_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    f = await db.get(Fine, fine_id)
    if not f:
        raise HTTPException(404, "Fine not found")
    await db.delete(f)
    await db.commit()
