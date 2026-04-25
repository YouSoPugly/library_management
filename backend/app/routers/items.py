from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_staff
from app.models.models import Author, ItemAuthor, ItemCopy, ItemTitle
from app.schemas.schemas import (
    AuthorCreate, AuthorOut,
    ItemAuthorCreate,
    ItemCopyCreate, ItemCopyOut, ItemCopyUpdate,
    ItemTitleCreate, ItemTitleOut,
)

# ITEM TITLES

items_router = APIRouter(prefix="/items", tags=["Catalog"])


@items_router.get("/", response_model=List[ItemTitleOut])
async def list_items(
    media_type: str | None = None,
    is_electronic: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(ItemTitle)
    if media_type:
        q = q.where(ItemTitle.media_type == media_type)
    if is_electronic is not None:
        q = q.where(ItemTitle.is_electronic == is_electronic)
    return (await db.execute(q)).scalars().all()


@items_router.post("/", response_model=ItemTitleOut, status_code=201)
async def create_item(body: ItemTitleCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    item = ItemTitle(**body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@items_router.get("/{item_id}", response_model=ItemTitleOut)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    item = await db.get(ItemTitle, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@items_router.put("/{item_id}", response_model=ItemTitleOut)
async def update_item(item_id: int, body: ItemTitleCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    item = await db.get(ItemTitle, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    for k, v in body.model_dump().items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return item


@items_router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    item = await db.get(ItemTitle, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    await db.delete(item)
    await db.commit()


# AUTHORS

authors_router = APIRouter(prefix="/authors", tags=["Catalog"])


@authors_router.get("/", response_model=List[AuthorOut])
async def list_authors(db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    return (await db.execute(select(Author))).scalars().all()


@authors_router.post("/", response_model=AuthorOut, status_code=201)
async def create_author(body: AuthorCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    a = Author(**body.model_dump())
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a


@authors_router.get("/{author_id}", response_model=AuthorOut)
async def get_author(author_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    a = await db.get(Author, author_id)
    if not a:
        raise HTTPException(404, "Author not found")
    return a


@authors_router.delete("/{author_id}", status_code=204)
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    a = await db.get(Author, author_id)
    if not a:
        raise HTTPException(404, "Author not found")
    await db.delete(a)
    await db.commit()


# ITEM <-> AUTHOR  (many-to-many)

item_authors_router = APIRouter(prefix="/item-authors", tags=["Catalog"])


@item_authors_router.post("/", status_code=201)
async def assign_author(body: ItemAuthorCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    ia = ItemAuthor(**body.model_dump())
    db.add(ia)
    await db.commit()
    return {"detail": "Author assigned to item"}


@item_authors_router.delete("/", status_code=204)
async def remove_author(item_id: int, author_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    ia = await db.get(ItemAuthor, (item_id, author_id))
    if not ia:
        raise HTTPException(404, "Mapping not found")
    await db.delete(ia)
    await db.commit()


# ITEM COPIES

copies_router = APIRouter(prefix="/copies", tags=["Catalog"])


@copies_router.get("/", response_model=List[ItemCopyOut])
async def list_copies(
    item_id: int | None = None,
    library_id: int | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_staff),
):
    q = select(ItemCopy)
    if item_id:
        q = q.where(ItemCopy.item_id == item_id)
    if library_id:
        q = q.where(ItemCopy.library_id == library_id)
    if status:
        q = q.where(ItemCopy.status == status)
    return (await db.execute(q)).scalars().all()


@copies_router.post("/", response_model=ItemCopyOut, status_code=201)
async def create_copy(body: ItemCopyCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = ItemCopy(**body.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@copies_router.get("/{copy_id}", response_model=ItemCopyOut)
async def get_copy(copy_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(ItemCopy, copy_id)
    if not c:
        raise HTTPException(404, "Copy not found")
    return c


@copies_router.patch("/{copy_id}", response_model=ItemCopyOut)
async def update_copy(copy_id: int, body: ItemCopyUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(ItemCopy, copy_id)
    if not c:
        raise HTTPException(404, "Copy not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c


@copies_router.delete("/{copy_id}", status_code=204)
async def delete_copy(copy_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_staff)):
    c = await db.get(ItemCopy, copy_id)
    if not c:
        raise HTTPException(404, "Copy not found")
    await db.delete(c)
    await db.commit()
