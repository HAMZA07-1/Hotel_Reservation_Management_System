"""
Module: test_database_manager.py
Date: 11/21/2025
Programmer(s): Hamza, Allen, Keano

Brief Description:
This module contains unit tests for the `DatabaseManager` class using Python's `unittest` framework. It verifies the correctness of the low-level database access layer, including connection management, schema creation, and all CRUD (Create, Read, Update, Delete) operations.

Class: TestDatabaseManager
Brief Description: A test suite that isolates the `DatabaseManager` for testing.

Important Functions:
- setUpClass() -> None
  - Input: None
  - Output: None
  - Description: A `unittest` class method that runs once before all tests. It creates a temporary, separate database file (`test_hotel.db`) to ensure that the tests are isolated and do not affect the main development database.
- tearDownClass() -> None
  - Input: None
  - Output: None
  - Description: Runs once after all tests are complete to clean up by deleting the temporary database file.
- test_...() methods: Each method tests a specific piece of functionality. For example:
  - `test_table_creation()`: Verifies that the database initialization correctly creates the required tables.
  - `test_insert_guest()` / `test_insert_room_lookup()`: Test the creation and subsequent retrieval of records.
  - `test_is_room_available()`: A critical test that verifies the room availability logic by creating a reservation and then checking for availability during overlapping and non-overlapping date ranges.

Important Data Structures:
- In-memory/Temporary Database: The tests are executed against a temporary SQLite database (`test_hotel.db`) to ensure test isolation and prevent data corruption.

Algorithms:
- Test Isolation: The use of `setUpClass` and `tearDownClass` implements a standard testing pattern. It ensures that all tests run against a clean, predictable database state, making the test results reliable and repeatable. This is superior to running tests against a live, changing database.
"""

import unittest
import os
import sqlite3
from database_manager import DatabaseManager

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
        self.db_manager.add_guest("Hamza", "Ashraf", "hamza@email.com", "555-5555", "Northridge")
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
    
    def test_insert_reservation(self):
        """create a guest and room, then insert a reservation"""
        self.db.add_guest('Alice', 'Smith', 'alice@example.com', '123', '1 Road')
        guest = self.db.get_guest(email='alice@example.com')
        self.assertIsNotNone(guest)

        self.db.add_room(room_number=201, room_type='Double', capacity=2, price=80.0, available=1)
        room = self.db.get_room(room_number=201)
        self.assertIsNotNone(room)

        res_id = self.db.add_reservation(
            guest_id=guest['guest_id'],
            room_id=room['room_id'],
            check_in_date='2025-12-01',
            check_out_date='2025-12-05',
            total_price=320.0,
            status='Confirmed'
        )
        self.assertIsInstance(res_id, int)

    def test_is_room_available(self):
        """create guest and room and test room availability"""
        self.db.add_guest('Bob', 'Jones', 'bob@example.com', '555', '2 Street')
        guest = self.db.get_guest(email='bob@example.com')

        self.db.add_room(room_number=301, room_type='Suite', capacity=4, price=200.0, available=1)
        room = self.db.get_room(room_number=301)

        # initially available
        self.assertTrue(self.db.is_room_available(room_number=301))

        # create a confirmed reservation that blocks 2025-11-10 to 2025-11-15
        self.db.add_reservation(
            guest_id=guest['guest_id'],
            room_id=room['room_id'],
            check_in_date='2025-11-10',
            check_out_date='2025-11-15',
            total_price=1000.0,
            status='Confirmed'
        )

        # overlapping ranges should be unavailable
        self.assertFalse(self.db.is_room_available(room_number=301, check_in_date='2025-11-12', check_out_date='2025-11-13'))

        # adjacent non-overlapping ranges should be available
        self.assertTrue(self.db.is_room_available(room_number=301, check_in_date='2025-11-15', check_out_date='2025-11-20'))


if __name__ == "__main__":
    unittest.main()
