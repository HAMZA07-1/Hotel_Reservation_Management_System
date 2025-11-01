
"""
Hotel Management Application
Room, Guest, and Reservation Classes
"""
from datetime import datetime
import sqlite3

class Room:
    def __init__(self, room_id, room_number, room_type, capacity, price, is_available):
        self.room_id = room_id
        self.room_number = room_number
        self.room_type = room_type
        self.capacity = capacity
        self.price = price
        self.is_available = is_available

    #Set method
    def set_room_id(self, room_id):
        self.room_id = room_id
    def set_number(self, room_number):
        self.room_number = room_number
    def set_type(self, room_type):
        self.room_type = room_type
    def set_capacity(self, capacity):
        self.capacity = capacity
    def set_price(self, price):
        self.price = price
    def set_available(self, is_available):
        self.is_available = is_available


class Reservation:
    STATUSES = ("Confirmed", "Checked-in", "Checked-out", "Cancelled", "No-show") #Revise later if all of these are needed

    def __init__(self, reservation_id, guest, room, check_in_date, check_out_date, status="Confirmed", total_price=None):
        self.reservation_id = reservation_id
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.set_status(status)
        self.total_price = total_price

    #Set methods
    def set_reservation_id(self, reservation_id):
        self.reservation_id = reservation_id
    def set_guest(self, guest):
        self.guest = guest
    def set_room(self, room):
        self.room = room
    def set_check_in_date(self, check_in_date):
        self.check_in_date = check_in_date
    def set_check_out_date(self, check_out_date):
        self.check_out_date = check_out_date
    def set_status(self, status):
        if status not in self.STATUSES:
            raise ValueError(f"Invalid Status: {status}")
        self.status = status


class Guest:
    def __init__(self, first_name, last_name, guest_id, email, phone, address):
        self.first_name = first_name
        self.last_name = last_name
        self.guest_id = guest_id
        self.email = email
        self.phone = phone
        self.address = address


    #Set methods
    def set_first_name(self, first_name):
        self.first_name = first_name
    def set_last_name(self, last_name):
        self.last_name = last_name
    def set_guest_id(self, guest_id):
        self.guest_id = guest_id
    def set_email(self, email):
        self.email = email
    def set_phone(self, phone):
        self.phone = phone
    def set_address(self, address):
        self.address = address



class DatabaseManager:
    def __init__(self, room_db, guest_db):
        self.room_db = room_db
        self.guest_db = guest_db

