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

import unittest
import os
import sqlite3
from database_manager import DatabaseManager
from hotel_manager import HotelManager

class TestDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Runs once before all tests — creates a temporary test DB file."""
        cls.test_db = "test_hotel.db"
        # Remove file if lingering from previous runs for deterministic setup
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass
        cls.db_manager = DatabaseManager(db_name=cls.test_db)
        # Provide simple alias used by some tests
        cls.db = cls.db_manager

    @classmethod
    def tearDownClass(cls):
        """Runs once after all tests — deletes the test DB file."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_database_connection(self):
        """Test if a connection to the SQLite database can be established."""
        conn = self.db_manager.connect()
        self.assertIsNotNone(conn)
        conn.close()

    def test_table_creation(self):
        """Check that required tables exist after setup."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()

        self.assertIn("rooms", tables)
        self.assertIn("guests", tables)

    def test_insert_room_basic(self):
        """Test inserting a room record."""
        self.db_manager.add_room(101, "Single", 1, 80.0, True)
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms WHERE room_number = 101;")
        room = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(room)
        self.assertEqual(int(room[1]), 101)

    def test_insert_guest(self):
        """Test inserting a guest record."""
        self.db_manager.add_guest("Hamza", "Ashraf", "hamza@email.com", "4622 McVaney Road", "Northridge", "CA", "91324", "555-5555-5555", "Apt 10")
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guests WHERE first_name = 'Hamza';")
        guest = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(guest)
        self.assertEqual(guest[1], "Hamza")
    
    def test_insert_room_lookup(self):
        """insert a room and verify it can be retrieved"""
        self.db.add_room(room_number=102, room_type='Single', capacity=1, price=50.0, available=1)
        room = self.db.get_room(room_number=102)
        self.assertIsNotNone(room)
        self.assertEqual(int(room['room_number']), 102)
        self.assertEqual(room['room_type'], 'Single')
        self.assertEqual(int(room['capacity']), 1)


    def test_is_room_available(self):
        """create guest and room and test room availability"""
        self.db.add_guest('Bob', 'Jones', 'bob@example.com', '1168 Haul Road', 'Mountain View', 'CA', '94041', '951-591-6654', 'Apt 5')
        guest = self.db.get_guest(email='bob@example.com')

        self.db.add_room(room_number=301, room_type='Suite', capacity=4, price=200.0, available=1)
        room = self.db.get_room(room_number=301)

        # initially available
        self.assertTrue(self.db.is_room_available(room_number=301))

        # create a confirmed reservation that blocks 2025-11-10 to 2025-11-15
        mgr = HotelManager(db_name=self.test_db)
        mgr.reserve_room(
            guest_id=guest['guest_id'],
            room_id=room['room_id'],
            check_in='2025-11-10',
            check_out='2025-11-15',
        )

        # overlapping ranges should be unavailable
        self.assertFalse(self.db.is_room_available(room_number=301, check_in_date='2025-11-12', check_out_date='2025-11-13'))

        # adjacent non-overlapping ranges should be available
        self.assertTrue(self.db.is_room_available(room_number=301, check_in_date='2025-11-15', check_out_date='2025-11-20'))


if __name__ == "__main__":
    unittest.main()
