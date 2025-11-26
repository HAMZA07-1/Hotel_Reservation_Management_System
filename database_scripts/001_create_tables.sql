-- Module: 001_create_tables.sql
-- Date: 11/1/2025
-- Programmer(s): Daniel, Keano, Hamza, Allen
--
-- Description:
-- This SQL script defines the complete database schema for the Hotel Reservation System. It contains the
-- CREATE TABLE statements for the core entities: rooms, guests, and reservations. It also establishes
-- column data types, primary keys, NOT NULL constraints, CHECK constraints for data integrity, and foreign
-- key relationships to enforce relational integrity between the tables.
--
-- Important Statements:
-- - CREATE TABLE rooms: Defines the structure for storing room inventory, including properties like room number,
--   type, capacity, price, and availability status.
-- - CREATE TABLE guests: Defines the structure for storing guest contact information.
-- - CREATE TABLE reservations: A linking table that connects a guest to a room for a specific date range.
--   It includes foreign keys that reference the guests and rooms tables.
-- - FOREIGN KEY ... ON DELETE CASCADE: Ensures that if a guest or room is deleted, all associated reservations
--   are also automatically deleted, maintaining data consistency.
-- - CREATE INDEX: Creates indexes on foreign key columns in the reservations table to improve the performance
--   of queries that join or filter on guest_id and room_id.
--


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

-- 4. EMPLOYEES TABLE
CREATE TABLE IF NOT EXISTS employees(
    employee_id INTEGER PRIMARY KEY,
    employee_password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    role TEXT NOT NULL
);
