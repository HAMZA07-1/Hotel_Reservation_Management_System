import unittest
from hotel_models import Room
from hotel_models import Guest
from hotel_models import Reservation
from datetime import datetime

#Test order: Room, Guest, Reservation
#Room Test
class RoomTestCase(unittest.TestCase):

    #Intializaiton Test
    def test_room_initialization(self):
        room = Room(1, 101, "Non-Smoking", 4, 110, True)
        self.assertEqual(room.room_id, 1)
        self.assertEqual(room.room_number, 101)
        self.assertEqual(room.room_type, "Non-Smoking")
        self.assertEqual(room.capacity, 4)
        self.assertEqual(room.price, 110)
        self.assertTrue(room.is_available)

    #Set Methods Test
    def test_room_update_methods(self):
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

    #Initialization Test
    def test_guest_initialization(self):
        guest = Guest("Daniel", "Sweet", 90137, "daniel.sweet.734@my.csun.edu", "818-123-4567", "18111 Nordhoff Street Northridge, CA 91330")
        self.assertEqual(guest.first_name, "Daniel")
        self.assertEqual(guest.last_name, "Sweet")
        self.assertEqual(guest.email, "daniel.sweet.734@my.csun.edu")
        self.assertEqual(guest.phone, "818-123-4567")
        self.assertEqual(guest.address, "18111 Nordhoff Street Northridge, CA 91330")

    #Set Methods Test
    def test_guest_update_methods(self):
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

    #Initialization Test
    def test_reservation_initialization(self):
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





if __name__ == '__main__':
    unittest.main()
