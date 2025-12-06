"""
Unit tests for room availability covering:
- EC1: valid non-overlapping booking (allowed)
- EC2: overlapping booking with occupied reservation (blocked)

These tests create an in-memory SQLite DB, initialize minimal schema, insert a room and
an existing confirmed reservation (2025-12-10 -> 2025-12-15), and assert availability.
"""
import sqlite3
import unittest
from datetime import datetime

BLOCKING_STATUSES = ("Confirmed", "Checked-in")

def init_schema(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        is_available INTEGER NOT NULL DEFAULT 1
    )
    """)
    cur.execute("""
    CREATE TABLE reservations (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL,
        check_in_date TEXT NOT NULL,
        check_out_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    conn.commit()

def is_room_available(conn, room_number, check_in_iso, check_out_iso):
    """
    Returns True if the room exists, is marked available, and has no blocking
    reservation that overlaps [check_in, check_out). Uses ISO date strings YYYY-MM-DD.
    """
    check_in = datetime.strptime(check_in_iso, "%Y-%m-%d").date()
    check_out = datetime.strptime(check_out_iso, "%Y-%m-%d").date()
    if check_in >= check_out:
        raise ValueError("Invalid date range: check_in must be before check_out")

    cur = conn.cursor()
    cur.execute("SELECT is_available FROM rooms WHERE room_number = ?", (room_number,))
    row = cur.fetchone()
    if not row:
        # Room not found -> treat as unavailable for booking
        return False
    if row[0] == 0:
        return False

    cur.execute(
        "SELECT check_in_date, check_out_date FROM reservations WHERE room_number = ? AND status IN ({})"
        .format(",".join("?" for _ in BLOCKING_STATUSES)),
        (room_number, *BLOCKING_STATUSES)
    )
    for r_in, r_out in cur.fetchall():
        existing_in = datetime.strptime(r_in, "%Y-%m-%d").date()
        existing_out = datetime.strptime(r_out, "%Y-%m-%d").date()
        # Overlap condition: [check_in, check_out) overlaps [existing_in, existing_out)
        if (check_in < existing_out) and (existing_in < check_out):
            return False
    return True


class TestRoomAvailabilityEC1EC2(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_schema(self.conn)
        cur = self.conn.cursor()
        # insert room 101 available
        cur.execute("INSERT INTO rooms (room_number, is_available) VALUES (?, ?)", ("101", 1))
        # existing confirmed reservation 2025-12-10 -> 2025-12-15
        cur.execute(
            "INSERT INTO reservations (room_number, check_in_date, check_out_date, status) VALUES (?, ?, ?, ?)",
            ("101", "2025-12-10", "2025-12-15", "Confirmed")
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_ec1_non_overlapping_allowed(self):
        """EC1: Non-overlapping booking (2025-12-16 -> 2025-12-20) should be allowed."""
        available = is_room_available(self.conn, "101", "2025-12-16", "2025-12-20")
        self.assertTrue(available, "EC1 failed: expected room to be available for non-overlapping dates")

    def test_ec2_overlapping_blocked(self):
        """EC2: Overlapping booking (2025-12-12 -> 2025-12-14) should be blocked."""
        available = is_room_available(self.conn, "101", "2025-12-12", "2025-12-14")
        self.assertFalse(available, "EC2 failed: expected room to be unavailable for overlapping dates")


if __name__ == "__main__":
    unittest.main()