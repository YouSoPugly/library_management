#!/usr/bin/env python3
"""
proj2-fillSchema.py

Seeds the University Library database with sample data using SQLAlchemy.
"""

from __future__ import annotations

import os
import random
import string
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Tuple
from urllib.parse import quote_plus

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection

fake = Faker()
Faker.seed(42)
random.seed(42)

# Use environment variables when possible.
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "port": os.getenv("MYSQL_PORT", "3306"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "university_library"),
}

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_CONFIG['user'])}:"
    f"{quote_plus(DB_CONFIG['password'])}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
    f"{DB_CONFIG['database']}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

NUM_LOCATIONS = 3
LIBRARIES_PER_LOCATION = 1

NUM_STUDENTS = 40
NUM_FACULTY = 15
NUM_STAFF = 12

NUM_ROLES = 4
NUM_PERMISSIONS = 8

NUM_AUTHORS = 35
NUM_ITEM_TITLES = 50
MIN_COPIES_PER_TITLE = 1
MAX_COPIES_PER_TITLE = 4

NUM_HOLDS = 20
NUM_CHECKOUTS = 45
NUM_INTER_LIBRARY_LOANS = 12
NUM_FINES = 15

ROOMS_PER_LIBRARY = 4
NUM_ROOM_RESERVATIONS = 30

ITEM_COPY_STATUSES = ["Available", "Checked Out", "On hold", "Damaged", "Lost"]
HOLD_STATUSES = ["Active", "Fulfilled", "Cancelled", "Expired"]
ILL_STATUSES = ["Requested", "In Transit", "Completed", "Cancelled"]
ROOM_STATUSES = ["Available", "Unavailable", "Maintenance"]
RESERVATION_STATUSES = ["Reserved", "Completed", "Cancelled"]

MEDIA_TYPES = ["Book", "Journal", "DVD", "Magazine", "eBook"]
DEPARTMENTS = [
    "Computer Science",
    "Mathematics",
    "History",
    "Biology",
    "English",
    "Business",
    "Physics",
]

ROLE_NAMES = ["Librarian", "Manager", "Assistant", "Archivist"]
PERMISSION_NAMES = [
    "View Patron Data",
    "Manage Checkouts",
    "Manage Holds",
    "Manage Fines",
    "Manage Rooms",
    "Manage Inventory",
    "Manage Staff Roles",
    "View Reports",
]


def get_connection() -> Connection:
    return engine.connect()


def fetch_ids(conn: Connection, sql: str, params: dict | None = None) -> List[int]:
    result = conn.execute(text(sql), params or {})
    return [row[0] for row in result.fetchall()]


def clear_tables(conn: Connection) -> None:
    """
    Clears all data in child-to-parent order.
    Safe for reseeding after tables already exist.
    """
    tables = [
        "ROOM_RESERVATION",
        "FINE",
        "INTER_LIBRARY_LOAN",
        "HOLD",
        "CHECKOUT",
        "ITEM_COPY",
        "ITEM_AUTHOR",
        "AUTHOR",
        "ITEM_TITLE",
        "STAFF_ROLE",
        "ROLE_PERMISSION",
        "PERMISSION",
        "ROLE",
        "STAFF",
        "FACULTY",
        "STUDENT",
        "PATRON",
        "ROOM",
        "LIBRARY",
        "LOCATION",
        "UNIVERSITY",
    ]

    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in tables:
        conn.execute(text(f"DELETE FROM {table}"))
        conn.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


def seed_university(conn: Connection) -> int:
    result = conn.execute(
        text("INSERT INTO UNIVERSITY (name) VALUES (:name)"),
        {"name": "Central Texas College"},
    )
    return result.lastrowid


def seed_locations(conn: Connection, university_id: int) -> List[int]:
    rows = [
        {"name": "San Marcos Campus", "city": "San Marcos", "suburb_or_campus": "Main Campus", "university_id": university_id},
        {"name": "Round Rock Campus", "city": "Round Rock", "suburb_or_campus": "North Campus", "university_id": university_id},
        {"name": "Kyle Campus", "city": "Kyle", "suburb_or_campus": "South Campus", "university_id": university_id},
    ]

    conn.execute(
        text(
            """
            INSERT INTO LOCATION (name, city, suburb_or_campus, university_id)
            VALUES (:name, :city, :suburb_or_campus, :university_id)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT location_id FROM LOCATION ORDER BY location_id")


def seed_libraries(conn: Connection, location_ids: List[int]) -> List[int]:
    rows = []
    for i, location_id in enumerate(location_ids, start=1):
        rows.append({"name": f"Library {i}", "location_id": location_id})

    conn.execute(
        text(
            """
            INSERT INTO LIBRARY (name, location_id)
            VALUES (:name, :location_id)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT library_id FROM LIBRARY ORDER BY library_id")


def seed_patrons_students_faculty(
    conn: Connection, university_id: int
) -> Tuple[List[int], List[int], List[int]]:
    patron_ids: List[int] = []
    student_patron_ids: List[int] = []
    faculty_patron_ids: List[int] = []

    for _ in range(NUM_STUDENTS):
        email = fake.unique.email()
        phone = fake.phone_number()[:20]

        result = conn.execute(
            text(
                """
                INSERT INTO PATRON (patron_type, email, phone)
                VALUES (:patron_type, :email, :phone)
                """
            ),
            {"patron_type": "Student", "email": email, "phone": phone},
        )
        patron_id = result.lastrowid
        patron_ids.append(patron_id)
        student_patron_ids.append(patron_id)

        conn.execute(
            text(
                """
                INSERT INTO STUDENT (patron_id, first_name, last_name, university_id)
                VALUES (:patron_id, :first_name, :last_name, :university_id)
                """
            ),
            {
                "patron_id": patron_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "university_id": university_id,
            },
        )

    for _ in range(NUM_FACULTY):
        email = fake.unique.email()
        phone = fake.phone_number()[:20]

        result = conn.execute(
            text(
                """
                INSERT INTO PATRON (patron_type, email, phone)
                VALUES (:patron_type, :email, :phone)
                """
            ),
            {"patron_type": "Faculty", "email": email, "phone": phone},
        )
        patron_id = result.lastrowid
        patron_ids.append(patron_id)
        faculty_patron_ids.append(patron_id)

        conn.execute(
            text(
                """
                INSERT INTO FACULTY (patron_id, first_name, last_name, department, university_id)
                VALUES (:patron_id, :first_name, :last_name, :department, :university_id)
                """
            ),
            {
                "patron_id": patron_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "department": random.choice(DEPARTMENTS),
                "university_id": university_id,
            },
        )

    return patron_ids, student_patron_ids, faculty_patron_ids


def random_hash(length: int = 60) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def seed_staff(conn: Connection, library_ids: List[int]) -> List[int]:
    rows = []
    for _ in range(NUM_STAFF):
        rows.append(
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.unique.email(),
                "library_id": random.choice(library_ids),
                "hashed_password": random_hash(),  # fake hash
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO STAFF (first_name, last_name, email, library_id, hashed_password)
            VALUES (:first_name, :last_name, :email, :library_id, :hashed_password)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT staff_id FROM STAFF ORDER BY staff_id")


def seed_roles_permissions(conn: Connection) -> Tuple[List[int], List[int]]:
    conn.execute(
        text(
            """
            INSERT INTO ROLE (role_name)
            VALUES (:role_name)
            """
        ),
        [{"role_name": name} for name in ROLE_NAMES],
    )

    conn.execute(
        text(
            """
            INSERT INTO PERMISSION (permission_name)
            VALUES (:permission_name)
            """
        ),
        [{"permission_name": name} for name in PERMISSION_NAMES],
    )

    role_ids = fetch_ids(conn, "SELECT role_id FROM ROLE ORDER BY role_id")
    permission_ids = fetch_ids(conn, "SELECT permission_id FROM PERMISSION ORDER BY permission_id")
    return role_ids, permission_ids


def seed_role_permissions(conn: Connection, role_ids: List[int], permission_ids: List[int]) -> None:
    rows = []
    for role_id in role_ids:
        assigned = random.sample(permission_ids, k=random.randint(2, len(permission_ids)))
        for permission_id in assigned:
            rows.append({"role_id": role_id, "permission_id": permission_id})

    conn.execute(
        text(
            """
            INSERT INTO ROLE_PERMISSION (role_id, permission_id)
            VALUES (:role_id, :permission_id)
            """
        ),
        rows,
    )


def seed_staff_roles(conn: Connection, staff_ids: List[int], role_ids: List[int]) -> None:
    rows = []
    for staff_id in staff_ids:
        assigned = random.sample(role_ids, k=random.randint(1, 2))
        for role_id in assigned:
            rows.append({"staff_id": staff_id, "role_id": role_id})

    conn.execute(
        text(
            """
            INSERT INTO STAFF_ROLE (staff_id, role_id)
            VALUES (:staff_id, :role_id)
            """
        ),
        rows,
    )


def seed_authors(conn: Connection) -> List[int]:
    rows = [
        {"first_name": fake.first_name(), "last_name": fake.last_name()}
        for _ in range(NUM_AUTHORS)
    ]

    conn.execute(
        text(
            """
            INSERT INTO AUTHOR (first_name, last_name)
            VALUES (:first_name, :last_name)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT author_id FROM AUTHOR ORDER BY author_id")


def seed_item_titles(conn: Connection) -> List[int]:
    prefixes = [
        "Introduction to",
        "Advanced",
        "Foundations of",
        "Modern",
        "Practical",
        "Principles of",
        "Guide to",
    ]
    subjects = [
        "Databases",
        "Algorithms",
        "Programming",
        "Operating Systems",
        "Physics",
        "Chemistry",
        "History",
        "Literature",
        "Business",
        "Networks",
    ]

    rows = []
    for _ in range(NUM_ITEM_TITLES):
        rows.append(
            {
                "title": f"{random.choice(prefixes)} {random.choice(subjects)}",
                "media_type": random.choice(MEDIA_TYPES),
                "loc_classification": f"QA{random.randint(100,999)}.{random.randint(10,99)}",
                "publication_date": fake.date_between(start_date="-20y", end_date="today"),
                "is_electronic": random.choice([True, False]),
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO ITEM_TITLE
                (title, media_type, loc_classification, publication_date, is_electronic)
            VALUES
                (:title, :media_type, :loc_classification, :publication_date, :is_electronic)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT item_id FROM ITEM_TITLE ORDER BY item_id")


def seed_item_authors(conn: Connection, item_ids: List[int], author_ids: List[int]) -> None:
    rows = []
    used = set()

    for item_id in item_ids:
        num_authors = random.randint(1, 3)
        selected_authors = random.sample(author_ids, k=num_authors)
        for author_id in selected_authors:
            pair = (item_id, author_id)
            if pair not in used:
                used.add(pair)
                rows.append({"item_id": item_id, "author_id": author_id})

    conn.execute(
        text(
            """
            INSERT INTO ITEM_AUTHOR (item_id, author_id)
            VALUES (:item_id, :author_id)
            """
        ),
        rows,
    )


def seed_item_copies(conn: Connection, item_ids: List[int], library_ids: List[int]) -> List[Tuple[int, str]]:
    rows = []

    for item_id in item_ids:
        num_copies = random.randint(MIN_COPIES_PER_TITLE, MAX_COPIES_PER_TITLE)
        for _ in range(num_copies):
            status = random.choices(
                population=ITEM_COPY_STATUSES,
                weights=[65, 15, 8, 7, 5],
                k=1,
            )[0]

            rows.append(
                {
                    "item_id": item_id,
                    "library_id": random.choice(library_ids),
                    "status": status,
                    "available_for_checkout": status == "Available",
                }
            )

    conn.execute(
        text(
            """
            INSERT INTO ITEM_COPY (item_id, library_id, status, available_for_checkout)
            VALUES (:item_id, :library_id, :status, :available_for_checkout)
            """
        ),
        rows,
    )

    result = conn.execute(text("SELECT copy_id, status FROM ITEM_COPY ORDER BY copy_id"))
    return [(row[0], row[1]) for row in result.fetchall()]


def seed_checkouts(
    conn: Connection,
    patron_ids: List[int],
    item_copies: List[Tuple[int, str]],
) -> List[int]:
    rows = []

    checkout_candidates = [copy_id for copy_id, status in item_copies if status != "Lost"]
    chosen_copy_ids = random.sample(
        checkout_candidates,
        k=min(NUM_CHECKOUTS, len(checkout_candidates)),
    )

    for copy_id in chosen_copy_ids:
        checkout_date = fake.date_between(start_date="-180d", end_date="-10d")
        due_date = checkout_date + timedelta(days=random.choice([14, 21, 28]))

        returned = random.choice([True, True, True, False])
        if returned:
            return_date = due_date + timedelta(days=random.randint(-3, 20))
            if return_date < checkout_date:
                return_date = checkout_date
        else:
            return_date = None

        rows.append(
            {
                "patron_id": random.choice(patron_ids),
                "copy_id": copy_id,
                "checkout_date": checkout_date,
                "due_date": due_date,
                "return_date": return_date,
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO CHECKOUT (patron_id, copy_id, checkout_date, due_date, return_date)
            VALUES (:patron_id, :copy_id, :checkout_date, :due_date, :return_date)
            """
        ),
        rows,
    )

    active_copy_ids = fetch_ids(
        conn,
        """
        SELECT copy_id
        FROM CHECKOUT
        WHERE return_date IS NULL
        """
    )

    if active_copy_ids:
        placeholders = ",".join([f":id{i}" for i in range(len(active_copy_ids))])
        params = {f"id{i}": cid for i, cid in enumerate(active_copy_ids)}
        conn.execute(
            text(
                f"""
                UPDATE ITEM_COPY
                SET status = 'Checked Out', available_for_checkout = FALSE
                WHERE copy_id IN ({placeholders})
                """
            ),
            params,
        )

    return fetch_ids(conn, "SELECT checkout_id FROM CHECKOUT ORDER BY checkout_id")


def seed_holds(conn: Connection, patron_ids: List[int], item_ids: List[int]) -> None:
    rows = []
    used = set()

    while len(rows) < NUM_HOLDS:
        pair = (random.choice(patron_ids), random.choice(item_ids))
        if pair in used:
            continue
        used.add(pair)

        rows.append(
            {
                "patron_id": pair[0],
                "item_id": pair[1],
                "hold_date": fake.date_between(start_date="-120d", end_date="today"),
                "hold_status": random.choice(HOLD_STATUSES),
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO HOLD (patron_id, item_id, hold_date, hold_status)
            VALUES (:patron_id, :item_id, :hold_date, :hold_status)
            """
        ),
        rows,
    )


def seed_inter_library_loans(
    conn: Connection,
    item_copies: List[Tuple[int, str]],
    library_ids: List[int],
) -> None:
    rows = []
    valid_copy_ids = [copy_id for copy_id, status in item_copies if status != "Lost"]

    if not valid_copy_ids:
        return

    for _ in range(min(NUM_INTER_LIBRARY_LOANS, len(valid_copy_ids))):
        copy_id = random.choice(valid_copy_ids)
        source_library_id, destination_library_id = random.sample(library_ids, 2)

        start_date = fake.date_between(start_date="-120d", end_date="-15d")
        completed = random.choice([True, True, False])
        end_date = start_date + timedelta(days=random.randint(3, 14)) if completed else None

        status = random.choice(ILL_STATUSES)
        if end_date is None and status == "Completed":
            status = "In Transit"

        rows.append(
            {
                "copy_id": copy_id,
                "source_library_id": source_library_id,
                "destination_library_id": destination_library_id,
                "start_date": start_date,
                "end_date": end_date,
                "loan_status": status,
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO INTER_LIBRARY_LOAN
                (copy_id, source_library_id, destination_library_id, start_date, end_date, loan_status)
            VALUES
                (:copy_id, :source_library_id, :destination_library_id, :start_date, :end_date, :loan_status)
            """
        ),
        rows,
    )


def seed_fines(conn: Connection, patron_ids: List[int], checkout_ids: List[int]) -> None:
    if not checkout_ids:
        return

    selected_checkout_ids = random.sample(checkout_ids, k=min(NUM_FINES, len(checkout_ids)))
    rows = []
    reasons = ["Overdue", "Damaged Item", "Lost Item"]

    for checkout_id in selected_checkout_ids:
        rows.append(
            {
                "patron_id": random.choice(patron_ids),
                "checkout_id": checkout_id,
                "amount": Decimal(random.choice(["5.00", "10.00", "15.50", "20.00", "35.00", "50.00"])),
                "reason": random.choice(reasons),
                "assessed_date": fake.date_between(start_date="-90d", end_date="today"),
                "paid_status": random.choice([True, False]),
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO FINE
                (patron_id, checkout_id, amount, reason, assessed_date, paid_status)
            VALUES
                (:patron_id, :checkout_id, :amount, :reason, :assessed_date, :paid_status)
            """
        ),
        rows,
    )


def seed_rooms(conn: Connection, library_ids: List[int]) -> List[int]:
    rows = []

    for library_id in library_ids:
        for i in range(1, ROOMS_PER_LIBRARY + 1):
            rows.append(
                {
                    "library_id": library_id,
                    "room_name": f"Study Room {i}",
                    "status": random.choice(ROOM_STATUSES),
                    "capacity": random.randint(2, 12),
                }
            )

    conn.execute(
        text(
            """
            INSERT INTO ROOM (library_id, room_name, status, capacity)
            VALUES (:library_id, :room_name, :status, :capacity)
            """
        ),
        rows,
    )

    return fetch_ids(conn, "SELECT room_id FROM ROOM ORDER BY room_id")


def seed_room_reservations(conn: Connection, room_ids: List[int], patron_ids: List[int]) -> None:
    rows = []

    for _ in range(NUM_ROOM_RESERVATIONS):
        start_dt = fake.date_time_between(start_date="-30d", end_date="+14d")
        end_dt = start_dt + timedelta(hours=random.randint(1, 3))

        rows.append(
            {
                "room_id": random.choice(room_ids),
                "patron_id": random.choice(patron_ids),
                "start_time": start_dt,
                "end_time": end_dt,
                "reservation_status": random.choice(RESERVATION_STATUSES),
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO ROOM_RESERVATION
                (room_id, patron_id, start_time, end_time, reservation_status)
            VALUES
                (:room_id, :patron_id, :start_time, :end_time, :reservation_status)
            """
        ),
        rows,
    )


def main() -> None:
    try:
        with engine.begin() as conn:
            clear_tables(conn)

            university_id = seed_university(conn)
            location_ids = seed_locations(conn, university_id)
            library_ids = seed_libraries(conn, location_ids)

            patron_ids, _, _ = seed_patrons_students_faculty(conn, university_id)

            staff_ids = seed_staff(conn, library_ids)

            role_ids, permission_ids = seed_roles_permissions(conn)
            seed_role_permissions(conn, role_ids, permission_ids)
            seed_staff_roles(conn, staff_ids, role_ids)

            author_ids = seed_authors(conn)
            item_ids = seed_item_titles(conn)
            seed_item_authors(conn, item_ids, author_ids)

            item_copies = seed_item_copies(conn, item_ids, library_ids)
            checkout_ids = seed_checkouts(conn, patron_ids, item_copies)
            seed_holds(conn, patron_ids, item_ids)
            seed_inter_library_loans(conn, item_copies, library_ids)
            seed_fines(conn, patron_ids, checkout_ids)

            room_ids = seed_rooms(conn, library_ids)
            seed_room_reservations(conn, room_ids, patron_ids)

        print("Database seeded successfully.")

    except Exception as e:
        print(f"Error while seeding database: {e}")
        raise


if __name__ == "__main__":
    main()