
-- This script sets up the foundational database schema for the Hotel Reservation System.
-- It defines the core tables (Rooms, Guests, Reservations) needed for the MVP and beyond.


-- 1. ROOMS TABLE
-- Defines the inventory of available hotel rooms.

CREATE TABLE IF NOT EXISTS rooms (

    room_id INTEGER PRIMARY KEY,
    room_number TEXT NOT NULL,
    room_type TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    price REAL NOT NULL,
    is_available INTEGER NOT NULL
);

-- 2. GUESTS TABLE (Initial Skeleton for Future Use)
-- Define the guests table needed for reservation logic in Sprint 2.

CREATE TABLE IF NOT EXISTS guests (
    guest_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT
);


-- 3. RESERVATIONS TABLE (Initial Skeleton for Future Use)
-- Define the structure for future booking records (Sprint 2).

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in_date TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    total_price REAL NOT NULL, -- example: (price per night * nights) * (1 + tax rate)
    status TEXT NOT NULL -- example: Confirmed, Cancelled, No show, Checked-in, Checked-out

    -- Foreign Key Constraints (Links this table to Rooms and Guests)
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);