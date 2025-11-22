"""
Module: UnitTestFile.py
Date: 10/28/2025
Programmer(s): Daniel

Brief Description:
This module contains a suite of unit tests for the data model classes (Room, Guest, Reservation) and for
verifying the database schema itself. It uses Python's `unittest` framework to ensure that the basic data
structures and the database table layouts behave as expected.

Class: RoomTestCase, GuestTestcase, ReservationTest
Brief Description: These test classes verify the correct initialization and functionality of the setter methods
for the `Room`, `Guest`, and `Reservation` data model classes from `hotel_models.py`.

Class: TestDatabaseSchema
Brief Description: This test class directly inspects the live database schema to ensure it matches the design.

Important Functions:
- test_*_initialization(): These methods check that the constructors of the model classes correctly assign
  the initial values to the object's attributes.
- test_*_update_methods(): These methods test the "setter" functions of the model classes to ensure they
  correctly modify the object's state.
- test_*_table_schema(): These methods use the `PRAGMA table_info` command to query the database schema and
  assert that the columns and their data types match the expected structure.
- test_foreign_keys(): This method uses `PRAGMA foreign_key_list` to verify that the foreign key relationships
  in the `reservations` table are correctly defined.

Important Data Structures:
- N/A

Algorithms:
- Schema Introspection: The `TestDatabaseSchema` class uses a database inspection technique. Instead of assuming
  the schema is correct, it queries the database's metadata using SQLite's `PRAGMA` commands. This allows the
  tests to dynamically verify the structure of the tables, including column names, data types, and foreign
  key constraints, providing a powerful way to detect any discrepancies between the code and the actual
  database schema.
"""

import unittest
from hotel_models import Room
from hotel_models import Guest
from hotel_models import Reservation
from datetime import datetime
import sqlite3

#Test order: Room, Guest, Reservation
#Room Test
class RoomTestCase(unittest.TestCase):
    """Tests the Room data model class."""

    #Intializaiton Test
    def test_room_initialization(self):
        """Tests the initialization of the Room class."""
        room = Room(1, 101, "Non-Smoking", 4, 110, True)
        self.assertEqual(room.room_id, 1)
        self.assertEqual(room.room_number, 101)
        self.assertEqual(room.room_type, "Non-Smoking")
        self.assertEqual(room.capacity, 4)
        self.assertEqual(room.price, 110)
        self.assertTrue(room.is_available)

    #Set Methods Test
    def test_room_update_methods(self):
        """Tests the setter methods of the Room class."""
        room = Room(1, 101, "Non-Smoking", 4, 110, True)

        room.set_number(101)
        self.assertEqual(room.room_number, 101)

        room.set_type("Smoking")
        self.assertEqual(room.room_type, "Smoking")

        room.set_capacity(10)
        self.assertEqual(room.capacity, 10)

        room.set_price(1)
        self.assertEqual(room.price, 1)

        room.set_available(False)
        self.assertEqual(room.is_available, False)

#Guest Tests
class GuestTestcase(unittest.TestCase):
    """Tests the Guest data model class."""

    #Initialization Test
    def test_guest_initialization(self):
        """Tests the initialization of the Guest class."""
        guest = Guest("Daniel", "Sweet", 90137, "daniel.sweet.734@my.csun.edu", "818-123-4567", "18111 Nordhoff Street Northridge, CA 91330")
        self.assertEqual(guest.first_name, "Daniel")
        self.assertEqual(guest.last_name, "Sweet")
        self.assertEqual(guest.email, "daniel.sweet.734@my.csun.edu")
        self.assertEqual(guest.phone, "818-123-4567")
        self.assertEqual(guest.address, "18111 Nordhoff Street Northridge, CA 91330")

    #Set Methods Test
    def test_guest_update_methods(self):
        """Tests the setter methods of the Guest class."""
        guest = Guest("Daniel", "Sweet", 90137, "daniel.sweet.734@my.csun.edu", "818-123-4567","18111 Nordhoff Street Northridge, CA 91330")

        guest.set_first_name("George")
        self.assertEqual(guest.first_name, "George")
        guest.set_last_name("Smith")
        self.assertEqual(guest.last_name, "Smith")
        guest.set_guest_id(21948)
        self.assertEqual(guest.guest_id, 21948)
        guest.set_email("sweet.daniel.437@my.csun.edu")
        self.assertEqual(guest.email, "sweet.daniel.437@my.csun.edu")
        guest.set_phone("818-987-6543")
        self.assertEqual(guest.phone, "818-987-6543")
        guest.set_address("308 Westwood Plz, Los Angeles, CA 90095-8355")
        self.assertEqual(guest.address, "308 Westwood Plz, Los Angeles, CA 90095-8355")


#Reservation Tests
class ReservationTest(unittest.TestCase):
    """Tests the Reservation data model class."""

    #Initialization Test
    def test_reservation_initialization(self):
        """Tests the initialization of the Reservation class."""
        room = Room(1, 101, "Non-Smoking", 4, 110, True)
        guest = Guest("Daniel", "Sweet", 90137, "daniel.sweet.734@my.csun.edu", "818-123-4567", "18111 Nordhoff Street Northridge, CA 91330")
        reservation = Reservation(1234, guest, room, datetime(2025,9,30), datetime(2025,10, 2))
        self.assertEqual(reservation.reservation_id, 1234)
        self.assertEqual(reservation.guest, guest)
        self.assertEqual(reservation.room, room)
        self.assertEqual(reservation.check_in_date, datetime(2025,9,30))
        self.assertEqual(reservation.check_out_date, datetime(2025,10,2))

    #Update Methods Test
    def test_reservation_update_methods(self):
        """Tests the setter methods of the Reservation class."""
        room = Room(1, 101, "Non-Smoking", 4, 110, True)
        guest = Guest("Daniel", "Sweet", 90137, "daniel.sweet.734@my.csun.edu", "818-123-4567","18111 Nordhoff Street Northridge, CA 91330")
        reservation = Reservation(1234, guest, room, datetime(2025, 9, 30), datetime(2025, 10, 2))

        reservation.set_reservation_id(4321)
        self.assertEqual(reservation.reservation_id, 4321)
        better_guest = Guest("Keano", "Aquino", 91853, "good.worker@hotmail.com", "408-249-5398", "1083 South Winchester Boulevard, San Jose CA 95128")
        reservation.set_guest(better_guest)
        self.assertEqual(reservation.guest, better_guest)
        better_room = Room(2, 202, "Smoking", 12, 500, False)
        reservation.set_room(better_room)
        self.assertEqual(reservation.room, better_room)
        reservation.set_check_in_date(datetime(2025, 10, 31))
        self.assertEqual(reservation.check_in_date, datetime(2025, 10, 31))
        reservation.set_check_out_date(datetime(2025, 11, 21))
        self.assertEqual(reservation.check_out_date, datetime(2025, 11, 21))

#Database Schema Tests
class TestDatabaseSchema(unittest.TestCase):
    """Tests the live database schema to ensure it matches the design."""
    #Test Database connection
    def setUp(self):
        """Sets up the database connection for the tests."""
        self.conn = sqlite3.connect('hotel.db')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """Closes the database connection after the tests."""
        self.conn.close()

    #Tests expected column data
    def test_rooms_table_schema(self):
        """Tests that the rooms table schema matches the expected structure."""
        #Geting column info for rooms table
        #Rooms
        self.cursor.execute("PRAGMA table_info(rooms);")
        columns = {col[1]: col[2] for col in self.cursor.fetchall()}

        expected = {
            "room_id": "INTEGER",
            "room_number": "TEXT",
            "room_type": "TEXT",
            "smoking": "INTEGER",
            "capacity": "INTEGER",
            "price": "REAL",
            "is_available": "INTEGER",
        }
        self.assertEqual(columns, expected)

        #Guests
    def test_guests_table_schema(self):
        """Tests that the guests table schema matches the expected structure."""
        self.cursor.execute("PRAGMA table_info(guests);")
        columns = {col[1]: col[2] for col in self.cursor.fetchall()}

        expected = {
            "guest_id": "INTEGER",
            "first_name": "TEXT",
            "last_name": "TEXT",
            "email": "TEXT",
            "phone": "TEXT",
            "address": "TEXT",
        }
        self.assertEqual(columns, expected)

    #Reservations
    def test_reservations_table_schema(self):
        """Tests that the reservations table schema matches the expected structure."""
        self.cursor.execute("PRAGMA table_info(reservations);")
        columns = {col[1]: col[2] for col in self.cursor.fetchall()}

        expected = {
            "reservation_id": "INTEGER",
            "guest_id": "INTEGER",
            "room_id": "INTEGER",
            "check_in_date": "DATETIME",
            "check_out_date": "DATETIME",
            "total_price": "REAL",
            "status": "TEXT",
        }
        self.assertEqual(columns, expected)

    #Testing foreign keys for Reservation
    def test_foreign_keys(self):
        """Tests that the foreign keys in the reservations table are correctly defined."""
        self.cursor.execute("PRAGMA foreign_key_list(reservations);")
        fk_info = self.cursor.fetchall()

        fk_tables = [(fk[2], fk[3],fk[4]) for fk in fk_info]

        expected_fks = [
            ('guests', 'guest_id', 'guest_id'),
            ('rooms', 'room_id', 'room_id')
        ]
        self.assertEqual(fk_tables, expected_fks)







if __name__ == '__main__':
    unittest.main()
