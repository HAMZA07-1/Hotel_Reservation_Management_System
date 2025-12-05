"""
Module: test_database_manager.py
Date: 12/04/2025
Programmer(s): Hamza, Allen, Keano

Brief Description:
This module contains unit tests for the `DatabaseManager` class using Python's `unittest` framework. It verifies the correctness of the low-level database access layer, including connection management, schema creation, and CRUD (Create, Read, Update, Delete) operations for guests and rooms.

Class: TestDatabaseManager
Brief Description: A test suite that isolates the `DatabaseManager` for testing against a temporary database.

Important Functions:
- setUpClass() -> None
  - Input: None
  - Output: None
  - Description: A `unittest` class method that runs once before all tests. Creates a temporary database file (`test_hotel.db`) to ensure tests are isolated from the main development database.
- tearDownClass() -> None
  - Input: None
  - Output: None
  - Description: Runs once after all tests are complete to clean up by deleting the temporary database file.
- test_...() methods: Each method tests a specific piece of functionality.
  - `test_database_connection()`: Verifies that a connection to the SQLite database can be established.
  - `test_table_creation()`: Verifies that the database initialization correctly creates the required tables (rooms, guests).
  - `test_insert_room_basic()`: Tests inserting a room record into the database.
  - `test_insert_guest()`: Tests inserting a guest record with the updated schema (phone_number, address fields).
  - `test_insert_room_lookup()`: Tests room creation and retrieval via `get_room()`.
  - `test_is_room_available()`: Tests room availability logic by creating a reservation via `HotelManager.reserve_room()` and checking for availability during overlapping and non-overlapping date ranges.

Important Data Structures:
- Temporary Database: Tests are executed against a temporary SQLite database (`test_hotel.db`) to ensure test isolation and prevent data corruption.

Algorithms:
- Test Isolation: The use of `setUpClass` and `tearDownClass` implements a standard testing pattern. It ensures that all tests run against a clean, predictable database state, making the test results reliable and repeatable.

Notes:
- Reservation insertion is tested via `HotelManager.reserve_room()` (not `DatabaseManager.add_reservation()`) since reservation creation requires transactional safety handled at the business logic layer.
"""

import sqlite3
import pytest
from datetime import date
from pathlib import Path

from database_manager import DatabaseManager
from hotel_manager import HotelManager


# ---------------------------------------------------------
# FIXTURE — fresh DB + patched create_if_missing
# ---------------------------------------------------------
@pytest.fixture
def db(tmp_path, monkeypatch):
    """Fresh DB with manually-created schema."""
    db_file = tmp_path / "test.db"

    # Prevent auto SQL script loading
    monkeypatch.setattr(DatabaseManager, "create_if_missing", lambda self: None)

    manager = DatabaseManager(db_name=str(db_file))

    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number INTEGER,
            room_type TEXT,
            smoking INTEGER DEFAULT 0,
            capacity INTEGER,
            price REAL,
            is_available INTEGER
        );

        CREATE TABLE guests (
            guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone_number TEXT,
            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT
        );

        CREATE TABLE reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER,
            room_id INTEGER,
            check_in_date TEXT,
            check_out_date TEXT,
            num_guests INTEGER,
            total_price REAL,
            status TEXT,
            is_paid INTEGER,
            FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        );
        """
    )
    conn.commit()
    conn.close()

    return manager


# ---------------------------------------------------------
# FIXTURE — HotelManager tied to same DB
# ---------------------------------------------------------
@pytest.fixture
def hotel(db):
    """HotelManager using the same DatabaseManager instance."""
    return HotelManager(db=db)


# ---------------------------------------------------------
# GUEST TESTS
# ---------------------------------------------------------
def test_add_and_get_guest(db):
    gid = db.add_guest(
        "John", "Doe", "john@example.com", "555-1111",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    row = db.get_guest(guest_id=gid)
    assert row["first_name"] == "John"
    assert row["email"] == "john@example.com"


def test_guest_exists(db):
    gid = db.add_guest(
        "Jane", "Doe", "jane@example.com", "555-2222",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    assert db.guest_exists(guest_id=gid)
    assert db.guest_exists(email="jane@example.com")


# ---------------------------------------------------------
# ROOM TESTS
# ---------------------------------------------------------
def test_add_and_get_room(db):
    db.add_room(101, "Queen", 2, 100.0, 1)
    row = db.get_room(room_number=101)

    assert row["room_type"] == "Queen"
    assert row["capacity"] == 2
    assert row["price"] == 100.0


def test_room_exists(db):
    db.add_room(201, "King", 2, 150.0, 1)
    row = db.get_room(room_number=201)

    assert db.room_exists(room_id=row["room_id"])
    assert db.room_exists(room_number=201)


def test_get_room_price(db):
    db.add_room(301, "Suite", 4, 300.0, 1)
    room = db.get_room(room_number=301)

    assert db.get_room_price(room["room_id"]) == 300.0


# ---------------------------------------------------------
# RESERVATION TESTS (HotelManager reserve_room)
# ---------------------------------------------------------
def test_add_reservation(db, hotel):
    gid = db.add_guest(
        "Alice", "Smith", "alice@example.com", "555-3333",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    db.add_room(400, "Queen", 2, 120.0, 1)
    room = db.get_room(room_number=400)

    res_id = hotel.reserve_room(
        gid, room["room_id"], "2025-01-01", "2025-01-05",
        num_guests=2, status="Confirmed"
    )

    assert isinstance(res_id, int)


def test_cancel_reservation(db, hotel):
    gid = db.add_guest(
        "Bob", "Jones", "bob@example.com", "555-4444",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    db.add_room(500, "Queen", 2, 140.0, 1)
    room = db.get_room(room_number=500)

    res_id = hotel.reserve_room(
        gid, room["room_id"], "2025-02-01", "2025-02-04",
        num_guests=2
    )

    assert db.cancel_reservation(res_id, gid) is True
    assert db.cancel_reservation(res_id, gid) is False


def test_update_reservation(db, hotel):
    gid = db.add_guest(
        "Carl", "Kay", "carl@example.com", "555-5555",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    db.add_room(600, "Queen", 2, 150.0, 1)
    room = db.get_room(room_number=600)

    res_id = hotel.reserve_room(
        gid, room["room_id"], "2025-03-01", "2025-03-05",
        num_guests=2
    )

    updated = db.update_reservation(
        res_id,
        "2025-03-02",
        "2025-03-06",
        650.0,
        "Checked-in"
    )
    assert updated is True


# ---------------------------------------------------------
# AVAILABILITY TESTS
# ---------------------------------------------------------
def test_is_room_available_simple(db):
    db.add_room(800, "Queen", 2, 99.0, 1)
    assert db.is_room_available(800)


def test_is_room_available_with_reservation(db, hotel):
    db.add_room(900, "Queen", 2, 120.0, 1)
    room = db.get_room(room_number=900)

    gid = db.add_guest(
        "Tim", "Booker", "tim@example.com", "555-7777",
        "Addr1", "Addr2", "City", "ST", "00000"
    )

    hotel.reserve_room(
        gid, room["room_id"],
        "2025-05-10", "2025-05-15",
        num_guests=1
    )

    assert not db.is_room_available(900, "2025-05-12", "2025-05-14")
    assert db.is_room_available(900, "2025-05-16", "2025-05-18")


def test_get_available_rooms(db):
    db.add_room(1000, "Queen", 2, 150.0, 1)
    db.add_room(1001, "Queen", 4, 200.0, 1)

    check_in = date(2025, 6, 1)
    check_out = date(2025, 6, 3)

    rooms = db.get_available_rooms(check_in, check_out, num_guests=2, include_smoking=1)
    assert len(rooms) == 2

