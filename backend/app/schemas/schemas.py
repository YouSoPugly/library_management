"""
Pydantic v2 schemas (request bodies & response models) for all entities.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


# AUTH

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    staff_id: Optional[int] = None


# UNIVERSITY

class UniversityCreate(BaseModel):
    name: str

class UniversityOut(BaseModel):
    university_id: int
    name: str
    model_config = {"from_attributes": True}


# LOCATION

class LocationCreate(BaseModel):
    name: str
    city: str
    suburb_or_campus: Optional[str] = None
    university_id: int

class LocationOut(BaseModel):
    location_id: int
    name: str
    city: str
    suburb_or_campus: Optional[str]
    university_id: int
    model_config = {"from_attributes": True}


# LIBRARY

class LibraryCreate(BaseModel):
    name: str
    location_id: int

class LibraryOut(BaseModel):
    library_id: int
    name: str
    location_id: int
    model_config = {"from_attributes": True}


# PATRON

class PatronCreate(BaseModel):
    patron_type: str   # "Student" or "Faculty"
    email: EmailStr
    phone: Optional[str] = None

    @field_validator("patron_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("Student", "Faculty"):
            raise ValueError("patron_type must be 'Student' or 'Faculty'")
        return v

class PatronOut(BaseModel):
    patron_id: int
    patron_type: str
    email: str
    phone: Optional[str]
    model_config = {"from_attributes": True}


# STUDENT

class StudentCreate(BaseModel):
    patron_id: int
    first_name: str
    last_name: str
    university_id: int

class StudentOut(BaseModel):
    student_id: int
    patron_id: int
    first_name: str
    last_name: str
    university_id: int
    model_config = {"from_attributes": True}


# FACULTY

class FacultyCreate(BaseModel):
    patron_id: int
    first_name: str
    last_name: str
    department: Optional[str] = None
    university_id: int

class FacultyOut(BaseModel):
    faculty_id: int
    patron_id: int
    first_name: str
    last_name: str
    department: Optional[str]
    university_id: int
    model_config = {"from_attributes": True}


# STAFF

class StaffCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    library_id: int

class StaffOut(BaseModel):
    staff_id: int
    first_name: str
    last_name: str
    email: str
    library_id: int
    model_config = {"from_attributes": True}


# ROLE, PERMISSION

class RoleCreate(BaseModel):
    role_name: str

class RoleOut(BaseModel):
    role_id: int
    role_name: str
    model_config = {"from_attributes": True}

class PermissionCreate(BaseModel):
    permission_name: str

class PermissionOut(BaseModel):
    permission_id: int
    permission_name: str
    model_config = {"from_attributes": True}

class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int

class StaffRoleCreate(BaseModel):
    staff_id: int
    role_id: int


# ITEM TITLE, AUTHOR

class ItemTitleCreate(BaseModel):
    title: str
    media_type: str
    loc_classification: Optional[str] = None
    publication_date: Optional[date] = None
    is_electronic: bool = False

class ItemTitleOut(BaseModel):
    item_id: int
    title: str
    media_type: str
    loc_classification: Optional[str]
    publication_date: Optional[date]
    is_electronic: bool
    model_config = {"from_attributes": True}

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str

class AuthorOut(BaseModel):
    author_id: int
    first_name: str
    last_name: str
    model_config = {"from_attributes": True}

class ItemAuthorCreate(BaseModel):
    item_id: int
    author_id: int


# ITEM COPY

class ItemCopyCreate(BaseModel):
    item_id: int
    library_id: int
    status: str
    available_for_checkout: bool = True

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Available", "Checked Out", "On hold", "Damaged", "Lost"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

class ItemCopyUpdate(BaseModel):
    status: Optional[str] = None
    available_for_checkout: Optional[bool] = None

class ItemCopyOut(BaseModel):
    copy_id: int
    item_id: int
    library_id: int
    status: str
    available_for_checkout: bool
    model_config = {"from_attributes": True}


# CHECKOUT

class CheckoutCreate(BaseModel):
    patron_id: int
    copy_id: int
    checkout_date: date
    due_date: date

class CheckoutReturn(BaseModel):
    return_date: date

class CheckoutOut(BaseModel):
    checkout_id: int
    patron_id: int
    copy_id: int
    checkout_date: date
    due_date: date
    return_date: Optional[date]
    model_config = {"from_attributes": True}


# HOLD

class HoldCreate(BaseModel):
    patron_id: int
    item_id: int
    hold_date: date
    hold_status: str

class HoldUpdate(BaseModel):
    hold_status: str

class HoldOut(BaseModel):
    hold_id: int
    patron_id: int
    item_id: int
    hold_date: date
    hold_status: str
    model_config = {"from_attributes": True}


# INTER-LIBRARY LOAN

class InterLibraryLoanCreate(BaseModel):
    copy_id: int
    source_library_id: int
    destination_library_id: int
    start_date: date
    end_date: Optional[date] = None
    loan_status: str

class InterLibraryLoanUpdate(BaseModel):
    end_date: Optional[date] = None
    loan_status: Optional[str] = None

class InterLibraryLoanOut(BaseModel):
    loan_id: int
    copy_id: int
    source_library_id: int
    destination_library_id: int
    start_date: date
    end_date: Optional[date]
    loan_status: str
    model_config = {"from_attributes": True}


# FINE

class FineCreate(BaseModel):
    patron_id: int
    checkout_id: int
    amount: Decimal
    reason: str
    assessed_date: date

class FineUpdate(BaseModel):
    paid_status: bool

class FineOut(BaseModel):
    fine_id: int
    patron_id: int
    checkout_id: int
    amount: Decimal
    reason: str
    assessed_date: date
    paid_status: bool
    model_config = {"from_attributes": True}


# ROOM

class RoomCreate(BaseModel):
    library_id: int
    room_name: str
    status: str
    capacity: int

class RoomUpdate(BaseModel):
    status: Optional[str] = None
    capacity: Optional[int] = None

class RoomOut(BaseModel):
    room_id: int
    library_id: int
    room_name: str
    status: str
    capacity: int
    model_config = {"from_attributes": True}


# ROOM RESERVATION

class RoomReservationCreate(BaseModel):
    room_id: int
    patron_id: int
    start_time: datetime
    end_time: datetime
    reservation_status: str

class RoomReservationUpdate(BaseModel):
    reservation_status: str

class RoomReservationOut(BaseModel):
    reservation_id: int
    room_id: int
    patron_id: int
    start_time: datetime
    end_time: datetime
    reservation_status: str
    model_config = {"from_attributes": True}
