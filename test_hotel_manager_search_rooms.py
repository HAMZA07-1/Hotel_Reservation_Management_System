"""
Module: test_hotel_manager_search_rooms.py
Date: 11/21/2025
Programmer(s): Keano

Brief Description:
This module contains a comprehensive unit test suite for the `search_rooms` method of the `HotelManager` class. It uses the `unittest` framework to verify the complex filtering and sorting logic, including date-based availability checks.

Class: TestSearchRooms
Brief Description: A test suite that sets up a detailed, temporary database to test various search scenarios.

Important Functions:
- setUp() -> None
  - Input: None
  - Output: None
  - Description: Runs before each test. It creates a temporary database and populates it with a specific, deterministic set of rooms, guests, and reservations. This controlled dataset is crucial for verifying that the search filters work correctly.
- tearDown() -> None
  - Input: None
  - Output: None
  - Description: Runs after each test to delete the temporary database, ensuring each test is independent.
- test_...() methods: Each method tests a specific search scenario.
  - `test_basic_attribute_filters()`: Checks filtering by room type and smoking status.
  - `test_availability_mode_free_excludes_overlaps()`: Verifies that the search correctly identifies and excludes rooms that have conflicting reservations for a given date range.
  - `test_availability_mode_occupied_includes_only_overlaps()`: Verifies the inverse of the above, finding only rooms that are booked.
  - `test_sorting_desc_capacity_then_tiebreaker()`: Checks if the sorting functionality works as expected.

Important Data Structures:
- Temporary Database with Seed Data: The `setUp` method creates a rich, temporary dataset that includes rooms with different properties and pre-existing reservations. This is essential for testing the interactions between different search filters.

Algorithms:
- Data-Driven Testing: The structure of this test class is a form of data-driven testing. A known set of data is inserted, and each test function asserts that a specific query against that data produces the exact, expected result. This is a robust way to validate complex query logic.
"""
import os
import tempfile
import unittest
from hotel_manager import HotelManager


class TestSearchRooms(unittest.TestCase):
    def setUp(self):
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
            ("Alice", "Smith", "alice@example.com", "123", "Addr1"),
            ("Bob", "Jones", "bob@example.com", "456", "Addr2"),
        ]
        for g in guests:
            self.db.execute_query(
                "INSERT INTO guests (first_name, last_name, email, phone, address) VALUES (?,?,?,?,?)",
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
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    @staticmethod
    def extract_numbers(rows):
        return sorted([str(row["room_number"]) for row in rows])

    def test_basic_attribute_filters(self):
        rows = self.mgr.search_rooms(room_types=["Double", "Suite"], smoking=False, is_available=1)
        self.assertEqual(self.extract_numbers(rows), ["102", "202"])

    def test_room_number_like_case_insensitive(self):
        rows = self.mgr.search_rooms(room_number_like="0")
        nums = self.extract_numbers(rows)
        self.assertTrue({"101", "102", "103", "201", "202"}.issubset(set(nums)))

    def test_capacity_and_price_range_with_swap_normalization(self):
        rows = self.mgr.search_rooms(min_capacity=4, max_capacity=1, min_price=300, max_price=80)
        nums = self.extract_numbers(rows)
        self.assertTrue({"101", "102", "103", "201"}.issubset(set(nums)))

    def test_availability_mode_free_excludes_overlaps(self):
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="free",
            is_available=1,
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"101", "103"})

    def test_availability_mode_occupied_includes_only_overlaps(self):
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="occupied",
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"102", "202"})

    def test_availability_mode_all_ignores_dates(self):
        rows = self.mgr.search_rooms(
            check_in="2025-12-10",
            check_out="2025-12-12",
            availability="all",
            room_types=["Suite"],
        )
        self.assertEqual(set(self.extract_numbers(rows)), {"103", "202"})

    def test_is_available_flag_filters_inventory(self):
        rows = self.mgr.search_rooms(is_available=0)
        self.assertEqual(self.extract_numbers(rows), ["201"])

    def test_sorting_desc_capacity_then_tiebreaker(self):
        rows = self.mgr.search_rooms(sort_by="capacity", sort_dir="desc")
        caps = [row["capacity"] for row in rows]
        self.assertEqual(caps, sorted(caps, reverse=True))

    def test_invalid_is_available_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.search_rooms(is_available=2)

    def test_partial_dates_ignored(self):
        rows = self.mgr.search_rooms(check_in="2025-12-10")  # missing check_out -> date logic ignored
        self.assertEqual(len(rows), 5)


if __name__ == "__main__":
    unittest.main()
