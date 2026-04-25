"""
University Library API
======================
FastAPI backend for the university_library MySQL schema.

Authentication
--------------
All routes (except POST /auth/token and POST /auth/register) require a
Bearer JWT obtained by posting staff credentials to POST /auth/token.

    POST /auth/token
    Body (form): username=<staff email>  password=<password>
    Response:    { "access_token": "...", "token_type": "bearer" }

Include the token in subsequent requests:
    Authorization: Bearer <access_token>
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
from app.models import models  # noqa – ensures models are registered with Base

from app.routers.auth import router as auth_router
from app.routers.universities import router as universities_router
from app.routers.locations import router as locations_router
from app.routers.libraries import router as libraries_router
from app.routers.patrons import (
    patrons_router,
    students_router,
    faculty_router,
)
from app.routers.staff import (
    staff_router,
    roles_router,
    permissions_router,
    role_permissions_router,
    staff_roles_router,
)
from app.routers.items import (
    items_router,
    authors_router,
    item_authors_router,
    copies_router,
)
from app.routers.circulation import (
    checkouts_router,
    holds_router,
    ill_router,
    fines_router,
)
from app.routers.rooms import rooms_router, reservations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — nothing needed here when using pre-existing schema
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="University Library API",
    description=__doc__,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Auth
app.include_router(auth_router)

#  Location hierarchy
app.include_router(universities_router)
app.include_router(locations_router)
app.include_router(libraries_router)

#  People
app.include_router(patrons_router)
app.include_router(students_router)
app.include_router(faculty_router)
app.include_router(staff_router)

#  Access Control
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(role_permissions_router)
app.include_router(staff_roles_router)

#  Catalog
app.include_router(items_router)
app.include_router(authors_router)
app.include_router(item_authors_router)
app.include_router(copies_router)

#  Circulation
app.include_router(checkouts_router)
app.include_router(holds_router)
app.include_router(ill_router)
app.include_router(fines_router)

#  Rooms
app.include_router(rooms_router)
app.include_router(reservations_router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "University Library API is running"}
