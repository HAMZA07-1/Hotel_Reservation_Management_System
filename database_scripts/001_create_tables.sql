-- This script sets up the foundational database schema for the Hotel Reservation System.
-- It defines the core tables (Rooms, Guests, Reservations) needed for the MVP and sprint upgrades.

-- 1. ROOMS TABLE
CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY,
    room_number TEXT NOT NULL,
    room_type TEXT NOT NULL,
    smoking INTEGER NOT NULL CHECK (smoking IN (0, 1)),
    capacity INTEGER NOT NULL CHECK (capacity >= 1),
    price REAL NOT NULL CHECK (price > 0),
    is_available INTEGER NOT NULL CHECK (is_available IN (0, 1))
);

-- 2. GUESTS TABLE
CREATE TABLE IF NOT EXISTS guests (
    guest_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT
);

-- 3. RESERVATIONS TABLE
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in_date DATETIME NOT NULL,   -- 'YYYY-MM-DD'
    check_out_date DATETIME NOT NULL,  -- 'YYYY-MM-DD'
    total_price REAL NOT NULL,
    status TEXT NOT NULL,              -- Confirmed, Cancelled, Checked-in, Checked-out

    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

-- 3a. INDEXES FOR RESERVATIONS
CREATE INDEX IF NOT EXISTS idx_reservations_guest_id
ON reservations (guest_id);

CREATE INDEX IF NOT EXISTS idx_reservations_room_id
ON reservations (room_id);
