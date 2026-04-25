"""
SQLAlchemy ORM models for the university_library schema.
Mirrors proj2-makeSchema.sql exactly.
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, DateTime,
    Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ─────────────────────────────────────────────
# 1. UNIVERSITY / LOCATION / LIBRARY
# ─────────────────────────────────────────────

class University(Base):
    __tablename__ = "UNIVERSITY"

    university_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    locations: Mapped[List["Location"]] = relationship("Location", back_populates="university")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="university")
    faculty: Mapped[List["Faculty"]] = relationship("Faculty", back_populates="university")


class Location(Base):
    __tablename__ = "LOCATION"

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    suburb_or_campus: Mapped[Optional[str]] = mapped_column(String(100))
    university_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UNIVERSITY.university_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    university: Mapped["University"] = relationship("University", back_populates="locations")
    libraries: Mapped[List["Library"]] = relationship("Library", back_populates="location")


class Library(Base):
    __tablename__ = "LIBRARY"

    library_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LOCATION.location_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    location: Mapped["Location"] = relationship("Location", back_populates="libraries")
    staff: Mapped[List["Staff"]] = relationship("Staff", back_populates="library")
    item_copies: Mapped[List["ItemCopy"]] = relationship("ItemCopy", back_populates="library")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="library")


# ─────────────────────────────────────────────
# 2. PATRONS, STUDENTS, FACULTY, STAFF
# ─────────────────────────────────────────────

class Patron(Base):
    __tablename__ = "PATRON"

    patron_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_type: Mapped[str] = mapped_column(Enum("Student", "Faculty"), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="patron", uselist=False)
    faculty: Mapped[Optional["Faculty"]] = relationship("Faculty", back_populates="patron", uselist=False)
    checkouts: Mapped[List["Checkout"]] = relationship("Checkout", back_populates="patron")
    holds: Mapped[List["Hold"]] = relationship("Hold", back_populates="patron")
    fines: Mapped[List["Fine"]] = relationship("Fine", back_populates="patron")
    room_reservations: Mapped[List["RoomReservation"]] = relationship("RoomReservation", back_populates="patron")


class Student(Base):
    __tablename__ = "STUDENT"

    student_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    university_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UNIVERSITY.university_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    patron: Mapped["Patron"] = relationship("Patron", back_populates="student")
    university: Mapped["University"] = relationship("University", back_populates="students")


class Faculty(Base):
    __tablename__ = "FACULTY"

    faculty_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, unique=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    university_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("UNIVERSITY.university_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    patron: Mapped["Patron"] = relationship("Patron", back_populates="faculty")
    university: Mapped["University"] = relationship("University", back_populates="faculty")


class Staff(Base):
    __tablename__ = "STAFF"

    staff_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LIBRARY.library_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )

    library: Mapped["Library"] = relationship("Library", back_populates="staff")
    staff_roles: Mapped[List["StaffRole"]] = relationship("StaffRole", back_populates="staff")


# ─────────────────────────────────────────────
# 3. ACCESS CONTROL (RBAC)
# ─────────────────────────────────────────────

class Role(Base):
    __tablename__ = "ROLE"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    role_permissions: Mapped[List["RolePermission"]] = relationship("RolePermission", back_populates="role")
    staff_roles: Mapped[List["StaffRole"]] = relationship("StaffRole", back_populates="role")


class Permission(Base):
    __tablename__ = "PERMISSION"

    permission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permission_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    role_permissions: Mapped[List["RolePermission"]] = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "ROLE_PERMISSION"

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ROLE.role_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PERMISSION.permission_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")


class StaffRole(Base):
    __tablename__ = "STAFF_ROLE"

    staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("STAFF.staff_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ROLE.role_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )

    staff: Mapped["Staff"] = relationship("Staff", back_populates="staff_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="staff_roles")


# ─────────────────────────────────────────────
# 4. LIBRARY ITEMS / AUTHORS
# ─────────────────────────────────────────────

class ItemTitle(Base):
    __tablename__ = "ITEM_TITLE"

    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    loc_classification: Mapped[Optional[str]] = mapped_column(String(50))
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    is_electronic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    item_authors: Mapped[List["ItemAuthor"]] = relationship("ItemAuthor", back_populates="item")
    copies: Mapped[List["ItemCopy"]] = relationship("ItemCopy", back_populates="item")
    holds: Mapped[List["Hold"]] = relationship("Hold", back_populates="item")


class Author(Base):
    __tablename__ = "AUTHOR"

    author_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    item_authors: Mapped[List["ItemAuthor"]] = relationship("ItemAuthor", back_populates="author")


class ItemAuthor(Base):
    __tablename__ = "ITEM_AUTHOR"

    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ITEM_TITLE.item_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("AUTHOR.author_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True
    )

    item: Mapped["ItemTitle"] = relationship("ItemTitle", back_populates="item_authors")
    author: Mapped["Author"] = relationship("Author", back_populates="item_authors")


class ItemCopy(Base):
    __tablename__ = "ITEM_COPY"

    copy_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ITEM_TITLE.item_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LIBRARY.library_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("Available", "Checked Out", "On hold", "Damaged", "Lost"), nullable=False
    )
    available_for_checkout: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    item: Mapped["ItemTitle"] = relationship("ItemTitle", back_populates="copies")
    library: Mapped["Library"] = relationship("Library", back_populates="item_copies")
    checkouts: Mapped[List["Checkout"]] = relationship("Checkout", back_populates="copy")
    inter_library_loans: Mapped[List["InterLibraryLoan"]] = relationship("InterLibraryLoan", back_populates="copy")


# ─────────────────────────────────────────────
# 5. CHECKOUTS / HOLDS / ILL / FINES
# ─────────────────────────────────────────────

class Checkout(Base):
    __tablename__ = "CHECKOUT"
    __table_args__ = (
        CheckConstraint("due_date >= checkout_date", name="chk_checkout_dates"),
        CheckConstraint("return_date IS NULL OR return_date >= checkout_date", name="chk_return_date"),
    )

    checkout_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    copy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ITEM_COPY.copy_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[date]] = mapped_column(Date)

    patron: Mapped["Patron"] = relationship("Patron", back_populates="checkouts")
    copy: Mapped["ItemCopy"] = relationship("ItemCopy", back_populates="checkouts")
    fines: Mapped[List["Fine"]] = relationship("Fine", back_populates="checkout")


class Hold(Base):
    __tablename__ = "HOLD"

    hold_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ITEM_TITLE.item_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    hold_date: Mapped[date] = mapped_column(Date, nullable=False)
    hold_status: Mapped[str] = mapped_column(String(50), nullable=False)

    patron: Mapped["Patron"] = relationship("Patron", back_populates="holds")
    item: Mapped["ItemTitle"] = relationship("ItemTitle", back_populates="holds")


class InterLibraryLoan(Base):
    __tablename__ = "INTER_LIBRARY_LOAN"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="chk_ill_dates"),
    )

    loan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    copy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ITEM_COPY.copy_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    source_library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LIBRARY.library_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    destination_library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LIBRARY.library_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    loan_status: Mapped[str] = mapped_column(String(50), nullable=False)

    copy: Mapped["ItemCopy"] = relationship("ItemCopy", back_populates="inter_library_loans")
    source_library: Mapped["Library"] = relationship("Library", foreign_keys=[source_library_id])
    destination_library: Mapped["Library"] = relationship("Library", foreign_keys=[destination_library_id])


class Fine(Base):
    __tablename__ = "FINE"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_fine_amount"),
    )

    fine_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    checkout_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("CHECKOUT.checkout_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    assessed_date: Mapped[date] = mapped_column(Date, nullable=False)
    paid_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    patron: Mapped["Patron"] = relationship("Patron", back_populates="fines")
    checkout: Mapped["Checkout"] = relationship("Checkout", back_populates="fines")


# ─────────────────────────────────────────────
# 6. ROOMS / RESERVATIONS
# ─────────────────────────────────────────────

class Room(Base):
    __tablename__ = "ROOM"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="chk_room_capacity"),
    )

    room_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    library_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("LIBRARY.library_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    room_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    library: Mapped["Library"] = relationship("Library", back_populates="rooms")
    reservations: Mapped[List["RoomReservation"]] = relationship("RoomReservation", back_populates="room")


class RoomReservation(Base):
    __tablename__ = "ROOM_RESERVATION"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="chk_room_reservation_times"),
    )

    reservation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ROOM.room_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    patron_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("PATRON.patron_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reservation_status: Mapped[str] = mapped_column(String(50), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="reservations")
    patron: Mapped["Patron"] = relationship("Patron", back_populates="room_reservations")
