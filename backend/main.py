#!/usr/bin/env python3
"""
FastAPI API layer for Project Part 3: Queries
University Library System - Engineer Io / Group 10
"""

import os
from decimal import Decimal
from typing import Any
from urllib.parse import quote_plus

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "port": os.getenv("MYSQL_PORT", "3306"),
    "user": os.getenv("MYSQL_USER", "library_user"),
    "password": os.getenv("MYSQL_PASSWORD", "library_password"),
    "database": os.getenv("MYSQL_DATABASE", "university_library"),
}

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_CONFIG['user'])}:"
    f"{quote_plus(DB_CONFIG['password'])}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
    f"{DB_CONFIG['database']}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(
    title="University Library API",
    description="API layer for Project Part 3 business queries.",
    version="1.0.0",
)


def clean_value(value: Any) -> Any:
    """Convert database values into JSON-friendly values."""
    if isinstance(value, Decimal):
        return float(value)
    return value


def run_query(sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Runs a SQL query and returns rows as dictionaries."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [
                {key: clean_value(value) for key, value in row._mapping.items()}
                for row in result.fetchall()
            ]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "University Library API is running",
        "docs": "/docs",
        "database": DB_CONFIG["database"],
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/checkouts/current")
def get_current_checkouts() -> list[dict[str, Any]]:
    sql = """
        SELECT
            c.checkout_id,
            p.patron_id,
            p.patron_type,
            p.email,
            it.title,
            ic.copy_id,
            l.name AS library_name,
            c.checkout_date,
            c.due_date
        FROM CHECKOUT c
        JOIN PATRON p ON c.patron_id = p.patron_id
        JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
        JOIN ITEM_TITLE it ON ic.item_id = it.item_id
        JOIN LIBRARY l ON ic.library_id = l.library_id
        WHERE c.return_date IS NULL
        ORDER BY c.due_date ASC;
    """
    return run_query(sql)


@app.get("/checkouts/overdue")
def get_overdue_checkouts() -> list[dict[str, Any]]:
    sql = """
        SELECT
            c.checkout_id,
            p.patron_id,
            p.patron_type,
            p.email,
            it.title,
            c.checkout_date,
            c.due_date,
            DATEDIFF(CURRENT_DATE, c.due_date) AS days_overdue
        FROM CHECKOUT c
        JOIN PATRON p ON c.patron_id = p.patron_id
        JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
        JOIN ITEM_TITLE it ON ic.item_id = it.item_id
        WHERE c.return_date IS NULL
          AND c.due_date < CURRENT_DATE
        ORDER BY days_overdue DESC;
    """
    return run_query(sql)


@app.get("/inventory/available-by-library")
def get_available_inventory_by_library() -> list[dict[str, Any]]:
    sql = """
        SELECT
            l.library_id,
            l.name AS library_name,
            loc.name AS location_name,
            COUNT(ic.copy_id) AS available_copies
        FROM LIBRARY l
        JOIN LOCATION loc ON l.location_id = loc.location_id
        LEFT JOIN ITEM_COPY ic
            ON l.library_id = ic.library_id
            AND ic.status = 'Available'
        GROUP BY l.library_id, l.name, loc.name
        ORDER BY available_copies DESC;
    """
    return run_query(sql)


@app.get("/items/search")
def search_available_items(
    keyword: str = Query("database", description="Keyword to search for in item titles")
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            it.item_id,
            it.title,
            it.media_type,
            it.loc_classification,
            ic.copy_id,
            l.name AS library_name,
            ic.status
        FROM ITEM_TITLE it
        JOIN ITEM_COPY ic ON it.item_id = ic.item_id
        JOIN LIBRARY l ON ic.library_id = l.library_id
        WHERE LOWER(it.title) LIKE LOWER(:keyword)
          AND ic.status = 'Available'
        ORDER BY it.title, l.name;
    """
    return run_query(sql, {"keyword": f"%{keyword}%"})


@app.get("/reports/most-borrowed")
def get_most_borrowed_titles() -> list[dict[str, Any]]:
    sql = """
        SELECT
            it.item_id,
            it.title,
            it.media_type,
            COUNT(c.checkout_id) AS times_checked_out
        FROM CHECKOUT c
        JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
        JOIN ITEM_TITLE it ON ic.item_id = it.item_id
        GROUP BY it.item_id, it.title, it.media_type
        ORDER BY times_checked_out DESC;
    """
    return run_query(sql)


@app.get("/patrons/multiple-active-checkouts")
def get_patrons_with_multiple_active_checkouts(
    minimum: int = Query(1, ge=0, description="Only show patrons with more than this many active checkouts")
) -> list[dict[str, Any]]:
    sql = """
        SELECT
            p.patron_id,
            p.patron_type,
            p.email,
            COUNT(c.checkout_id) AS active_checkouts
        FROM PATRON p
        JOIN CHECKOUT c ON p.patron_id = c.patron_id
        WHERE c.return_date IS NULL
        GROUP BY p.patron_id, p.patron_type, p.email
        HAVING COUNT(c.checkout_id) > :minimum
        ORDER BY active_checkouts DESC;
    """
    return run_query(sql, {"minimum": minimum})


@app.get("/holds/active")
def get_active_holds() -> list[dict[str, Any]]:
    sql = """
        SELECT
            h.hold_id,
            it.title,
            p.patron_id,
            p.patron_type,
            p.email,
            h.hold_date,
            h.hold_status
        FROM HOLD h
        JOIN PATRON p ON h.patron_id = p.patron_id
        JOIN ITEM_TITLE it ON h.item_id = it.item_id
        WHERE h.hold_status = 'Active'
        ORDER BY it.title, h.hold_date ASC;
    """
    return run_query(sql)


@app.get("/fines/unpaid")
def get_unpaid_fines() -> list[dict[str, Any]]:
    sql = """
        SELECT
            p.patron_id,
            p.patron_type,
            p.email,
            COUNT(f.fine_id) AS unpaid_fine_count,
            SUM(f.amount) AS total_unpaid_fines
        FROM FINE f
        JOIN PATRON p ON f.patron_id = p.patron_id
        WHERE f.paid_status = FALSE
        GROUP BY p.patron_id, p.patron_type, p.email
        ORDER BY total_unpaid_fines DESC;
    """
    return run_query(sql)


@app.get("/loans/interlibrary")
def get_interlibrary_loans() -> list[dict[str, Any]]:
    sql = """
        SELECT
            ill.loan_id,
            it.title,
            ic.copy_id,
            source.name AS source_library,
            destination.name AS destination_library,
            ill.start_date,
            ill.end_date,
            ill.loan_status
        FROM INTER_LIBRARY_LOAN ill
        JOIN ITEM_COPY ic ON ill.copy_id = ic.copy_id
        JOIN ITEM_TITLE it ON ic.item_id = it.item_id
        JOIN LIBRARY source ON ill.source_library_id = source.library_id
        JOIN LIBRARY destination ON ill.destination_library_id = destination.library_id
        ORDER BY ill.start_date DESC;
    """
    return run_query(sql)


@app.get("/rooms/reservations")
def get_room_reservations() -> list[dict[str, Any]]:
    sql = """
        SELECT
            rr.reservation_id,
            r.room_name,
            r.capacity,
            l.name AS library_name,
            p.patron_id,
            p.patron_type,
            p.email,
            rr.start_time,
            rr.end_time,
            rr.reservation_status
        FROM ROOM_RESERVATION rr
        JOIN ROOM r ON rr.room_id = r.room_id
        JOIN LIBRARY l ON r.library_id = l.library_id
        JOIN PATRON p ON rr.patron_id = p.patron_id
        ORDER BY rr.start_time;
    """
    return run_query(sql)


@app.get("/reports/inventory-summary")
def get_inventory_summary() -> list[dict[str, Any]]:
    sql = """
        SELECT
            it.media_type,
            COUNT(ic.copy_id) AS total_copies,
            SUM(CASE WHEN ic.status = 'Available' THEN 1 ELSE 0 END) AS available_copies,
            SUM(CASE WHEN ic.status = 'Checked Out' THEN 1 ELSE 0 END) AS checked_out_copies,
            SUM(CASE WHEN ic.status = 'On hold' THEN 1 ELSE 0 END) AS on_hold_copies,
            SUM(CASE WHEN ic.status = 'Damaged' THEN 1 ELSE 0 END) AS damaged_copies,
            SUM(CASE WHEN ic.status = 'Lost' THEN 1 ELSE 0 END) AS lost_copies
        FROM ITEM_TITLE it
        JOIN ITEM_COPY ic ON it.item_id = ic.item_id
        GROUP BY it.media_type
        ORDER BY total_copies DESC;
    """
    return run_query(sql)


@app.get("/staff/roles")
def get_staff_roles() -> list[dict[str, Any]]:
    sql = """
        SELECT
            s.staff_id,
            s.first_name,
            s.last_name,
            s.email,
            l.name AS library_name,
            r.role_name
        FROM STAFF s
        JOIN LIBRARY l ON s.library_id = l.library_id
        JOIN STAFF_ROLE sr ON s.staff_id = sr.staff_id
        JOIN ROLE r ON sr.role_id = r.role_id
        ORDER BY s.last_name, s.first_name, r.role_name;
    """
    return run_query(sql)


@app.get("/roles/permissions")
def get_role_permissions() -> list[dict[str, Any]]:
    sql = """
        SELECT
            r.role_name,
            p.permission_name
        FROM ROLE r
        JOIN ROLE_PERMISSION rp ON r.role_id = rp.role_id
        JOIN PERMISSION p ON rp.permission_id = p.permission_id
        ORDER BY r.role_name, p.permission_name;
    """
    return run_query(sql)
