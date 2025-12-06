"""
Module: test_hotel_manager.py
Date: 12/04/2025
Programmer(s): Keano

Brief Description:
This module contains test suites for the `HotelManager` class. It uses the `unittest` framework to verify:
1. The complex filtering and sorting logic of `search_rooms` (integration test with temporary database).
2. The `reserve_room` method's validation and transactional logic (unit test with mocks).

Class: TestSearchRooms
Brief Description: An integration test suite that sets up a detailed, temporary database to test various search scenarios.

Important Functions:
- setUp() -> None
  - Input: None
  - Output: None
  - Description: Runs before each test. Creates a temporary database and populates it with a specific, deterministic set of rooms, guests, and reservations.
- tearDown() -> None
  - Input: None
  - Output: None
  - Description: Runs after each test to delete the temporary database, ensuring each test is independent.
- test_...() methods: Each method tests a specific search scenario.
  - `test_basic_attribute_filters()`: Checks filtering by room type and smoking status.
  - `test_availability_mode_free_excludes_overlaps()`: Verifies that the search correctly excludes rooms with conflicting reservations.
  - `test_availability_mode_occupied_includes_only_overlaps()`: Verifies the inverse, finding only rooms that are booked.
  - `test_sorting_desc_capacity_then_tiebreaker()`: Checks if the sorting functionality works as expected.
  - `test_invalid_is_available_raises()`: Tests that invalid 'is_available' values raise ValueError.
  - `test_partial_dates_ignored()`: Tests that partial date inputs ignore date-based availability filtering.

Class: TestReserveRoom
Brief Description: A unit test suite using mocks to test the `reserve_room` method's validation and transactional behavior.

Important Functions:
- setUp() -> None
  - Input: None
  - Output: None
  - Description: Runs before each test. Creates a HotelManager with a mocked DatabaseManager to isolate business logic.
- test_...() methods: Each method tests a specific reservation scenario.
  - `test_successful_reservation()`: Tests the ideal case where a reservation is successfully created.
  - `test_fails_if_guest_not_found()`: Tests validation when guest does not exist.
  - `test_fails_if_room_not_found()`: Tests validation when room does not exist.
  - `test_fails_if_num_guests_exceeds_capacity()`: Tests validation when num_guests exceeds room capacity.
  - `test_fails_if_room_is_unavailable_during_transaction()`: Tests the race condition handling when room becomes booked during transaction.

Important Data Structures:
- Temporary Database (TestSearchRooms): A controlled dataset with rooms, guests, and reservations for testing search filters.
- Mock DatabaseManager (TestReserveRoom): A mocked database layer to isolate and test business logic without actual database operations.

Algorithms:
- Data-Driven Testing (TestSearchRooms): Known data is inserted, and tests assert that queries produce exact, expected results.
- Behavior-Driven Testing (TestReserveRoom): Mocks simulate database responses to verify method behavior under various conditions.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from hotel_manager import HotelManager


class TestSearchRooms(unittest.TestCase):
    """A test suite for the HotelManager's search_rooms method."""

    def setUp(self):
        """Sets up a temporary database with seed data before each test."""
        # Create a temp file path (file pre-created; schema inspection will initialize if needed)
        fd, self.db_path = tempfile.mkstemp(prefix="search_rooms_", suffix=".db")
        os.close(fd)
        self.mgr = HotelManager(db_name=self.db_path)
        self.db = self.mgr.db
        # Ensure clean deterministic dataset
        self.db.execute_query("DELETE FROM reservations")
        self.db.execute_query("DELETE FROM rooms")
        self.db.execute_query("DELETE FROM guests")
        # Seed rooms: (room_number, room_type, capacity, price, smoking, is_available)
        rooms = [
            (101, "Single", 1, 80.0, 0, 1),
            (102, "Double", 2, 120.0, 0, 1),
            (103, "Suite", 4, 300.0, 1, 1),
            (201, "Double", 2, 110.0, 0, 0),
            (202, "Suite", 4, 320.0, 0, 1),
        ]
        for r in rooms:
            self.db.execute_query(
                "INSERT INTO rooms (room_number, room_type, capacity, price, smoking, is_available) VALUES (?,?,?,?,?,?)",
                r,
            )
        # Seed guests
        guests = [
            ("Alice", "Smith", "alice@example.com", "123-456-7890", "123 Main St", "Los Angeles", "CA", "90001"),
            ("Bob", "Jones", "bob@example.com", "456-789-0123", "456 Oak Ave", "San Diego", "CA", "92101"),
        ]
        for g in guests:
            self.db.execute_query(
                "INSERT INTO guests (first_name, last_name, email, phone_number, address_line1, city, state, postal_code) VALUES (?,?,?,?,?,?,?,?)",
                g,
            )
        # Map ids
        room_rows = self.db.execute_query("SELECT room_id, room_number FROM rooms")
        guest_rows = self.db.execute_query("SELECT guest_id, email FROM guests")
        num_to_id = {int(row["room_number"]): row["room_id"] for row in room_rows}
        email_to_id = {row["email"]: row["guest_id"] for row in guest_rows}
        # Seed overlapping reservations (Alice in 102, Bob in 202)
        self.db.execute_query(
            "INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status) VALUES (?,?,?,?,?,?)",
            (email_to_id["alice@example.com"], num_to_id[102], "2025-12-10", "2025-12-12", 240.0, "Confirmed"),
        )
        self.db.execute_query(
            "INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status) VALUES (?,?,?,?,?,?)",
            (email_to_id["bob@example.com"], num_to_id[202], "2025-12-11", "2025-12-13", 640.0, "Confirmed"),
        )

    def tearDown(self):
        """Removes the temporary database file after each test."""
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    @staticmethod
    def extract_numbers(rows):
        """A helper function to extract and sort room numbers from a list of room rows."""
        return sorted([str(row["room_number"]) for row in rows])

    def test_basic_attribute_filters(self):
        """Tests filtering by room type, smoking status, and availability."""
        rows = self.mgr.search_rooms(room_types=["Double", "Suite"], smoking=False, is_available=1)
        self.assertEqual(self.extract_numbers(rows), ["102", "202"])

    def test_room_number_like_case_insensitive(self):
        """Tests case-insensitive substring search for room numbers."""
        rows = self.mgr.search_rooms(room_number_like="0")
        nums = self.extract_numbers(rows)
        self.assertTrue({"101", "102", "103", "201", "202"}.issubset(set(nums)))

    def test_capacity_and_price_range_with_swap_normalization(self):
        """Tests that inverted min/max ranges for capacity and price are handled correctly."""
        rows = self.mgr.search_rooms(min_capacity=4, max_capacity=1, min_price=300, max_price=80)
        nums = self.extract_numbers(rows)
        self.assertTrue({"101", "102", "103", "201"}.issubset(set(nums)))

    def test_availability_mode_free_excludes_overlaps(self):
        """Tests that the 'free' availability mode correctly excludes rooms with overlapping reservations."""
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="free",
            is_available=1,
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"101", "103"})

    def test_availability_mode_occupied_includes_only_overlaps(self):
        """Tests that the 'occupied' availability mode correctly finds only rooms with overlapping reservations."""
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="occupied",
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"102", "202"})

    def test_availability_mode_all_ignores_dates(self):
        """Tests that the 'all' availability mode ignores date overlaps and returns all matching rooms."""
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="all",
            room_types=["Suite"],
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"103", "202"})

    def test_is_available_flag_filters_inventory(self):
        """Tests filtering for rooms that are marked as not available (e.g., for maintenance)."""
        rows = self.mgr.search_rooms(is_available=0)
        self.assertEqual(self.extract_numbers(rows), ["201"])

    def test_sorting_desc_capacity_then_tiebreaker(self):
        """Tests that sorting by capacity in descending order works correctly."""
        rows = self.mgr.search_rooms(sort_by="capacity", sort_dir="desc")
        caps = [row["capacity"] for row in rows]
        self.assertEqual(caps, sorted(caps, reverse=True))

    def test_invalid_is_available_raises(self):
        """Tests that providing an invalid value for 'is_available' raises a ValueError."""
        with self.assertRaises(ValueError):
            self.mgr.search_rooms(is_available=2)

    def test_partial_dates_ignored(self):
        """Tests that providing only a check-in or check-out date ignores date-based availability filtering."""
        rows = self.mgr.search_rooms(check_in="2025-12-10")  # missing check_out -> date logic ignored
        self.assertEqual(len(rows), 5)

class TestReserveRoom(unittest.TestCase):
    """A unit test for the HotelManager's reserve_room method."""

    def setUp(self):
        """Runs before each test. Creates a HotelManager with a fake database."""
        # Creates a mock for the DatabaseManager
        self.mock_db = MagicMock()
        # Inject the mock into the HotelManager
        self.mgr = HotelManager(db=self.mock_db)

    def test_fails_if_invalid_dates(self):
        """Tests that the method correctly stops if the dates are invalid"""
        # Test 1: check_out before check_in
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=1, check_in="2025-12-05", check_out="2025-12-01")
        self.assertEqual(str(context.exception), "check_out must be after check_in.")

        # Test 2: same day check_in and check_out
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=1, check_in="2025-12-01", check_out="2025-12-01")
        self.assertEqual(str(context.exception), "check_out cannot be the same day as check_in.")

        # Test 3: invalid date format
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=1, check_in="12-01-2025", check_out="12-05-2025")
        self.assertEqual(str(context.exception), "Invalid date format. Use YYYY-MM-DD.")

    def test_fails_if_guest_not_found(self):
        """Tests that the method correctly stops if the guest does not exist."""
        # Arrange
        self.mock_db.guest_exists.return_value = False

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=999, room_id=1, check_in="2025-12-01", check_out="2025-12-02")
        self.assertEqual(str(context.exception), "Guest does not exist.")

    def test_fails_if_room_not_found(self):
        """Tests that the method correctly stops if the room does not exist."""
        # Arrange
        self.mock_db.guest_exists.return_value = True
        self.mock_db.room_exists.return_value = False

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=999, check_in="2025-12-01", check_out="2025-12-02")
        self.assertEqual(str(context.exception), "Room does not exist.")

    def test_fails_if_num_guests_exceeds_capacity(self):
        """Tests that reservation fails when num_guests exceeds room capacity."""
        # Arrange
        self.mock_db.guest_exists.return_value = True
        self.mock_db.room_exists.return_value = True
        self.mock_db.get_room.return_value = {"price": 100.0, "capacity": 2}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=1, check_in="2025-12-01", check_out="2025-12-03", num_guests=5)
        self.assertEqual(str(context.exception), "Number of guests exceeds room capacity.")

    def test_fails_if_room_is_unavailable_during_transaction(self):
        """Tests the race condition: the room becomes booked at the last second."""
        # Arrange
        self.mock_db.guest_exists.return_value = True
        self.mock_db.room_exists.return_value = True
        self.mock_db.get_room.return_value = {"price": 100.0}
        mock_conn = self.mock_db.connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1, )

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.mgr.reserve_room(guest_id=1, room_id=1, check_in="2025-12-01", check_out="2025-12-03")

        self.assertEqual(str(context.exception), "Room is no longer available for the selected dates")
        mock_cursor.execute.assert_any_call("ROLLBACK")

    def test_successful_reservation(self):
        """Tests the ideal case: everything works and a reservation is made."""
        # Arrange
        self.mock_db.guest_exists.return_value = True
        self.mock_db.room_exists.return_value = True
        self.mock_db.get_room.return_value = {"price": 100.0}
        mock_conn = self.mock_db.connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None
        mock_cursor.lastrowid = 42

        # Act
        reservation_id = self.mgr.reserve_room(guest_id=1, room_id=1, check_in="2025-12-01", check_out="2025-12-03")

        # Assert
        self.assertEqual(reservation_id, 42)
        mock_cursor.execute.assert_any_call("BEGIN IMMEDIATE")
        mock_cursor.execute.assert_any_call("COMMIT")
        self.assertNotIn(unittest.mock.call("ROLLBACK"), mock_cursor.execute.call_args_list)

if __name__ == "__main__":
    unittest.main()
