"""
Database Manager Unit Tests
Checks that SQLite connections, table creation, and CRUD operations work.
This test uses a temporary database to avoid modifying real data.
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
        cls.db_manager = DatabaseManager(db_name=cls.test_db)
        cls.db_manager.create_tables()

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

    def test_insert_room(self):
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

if __name__ == "__main__":
    unittest.main()
