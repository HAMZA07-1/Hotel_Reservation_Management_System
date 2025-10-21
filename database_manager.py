import sqlite3
import os

# This file handles all the database stuff like creating tables and
# saving/fetching room or reservation info.
class DatabaseManager:
    def __init__(self, db_file="hotel_data.db"):
        self.db_file = db_file
        self.create_if_missing()

    def create_if_missing(self):
        """Make sure the database and tables exist before we start."""
        create_script = "database_scripts/001_create_tables.sql"
        populate_script = "database_scripts/002_populate_rooms.sql"

        # If the db doesn't exist yet, create it and add the base data
        if not os.path.exists(self.db_file):
            print("Setting up the hotel database...")
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            try:
                with open(create_script, "r") as file:
                    c.executescript(file.read())
                with open(populate_script, "r") as file:
                    c.executescript(file.read())
                conn.commit()
                print("Database created successfully.")
            except Exception as e:
                print("Error during DB setup:", e)
            finally:
                conn.close()
        else:
            print("(i) Database already exists. Skipping setup.")

    def connect(self):
        """Return a new connection (make sure to close after use)."""
        return sqlite3.connect(self.db_file)

    # ---------- ROOM FUNCTIONS ----------
    def add_room(self, number, rtype, capacity, price, available):
        """Insert a new room (mostly for testing or setup)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rooms (room_number, room_type, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?)
        """, (number, rtype, capacity, price, available))
        conn.commit()
        conn.close()

    def get_all_rooms(self):
        """Grab all room info (for the room status window)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM rooms")
        data = cur.fetchall()
        conn.close()
        return data

    def change_room_status(self, room_id, available):
        """Change whether a room is available (1) or occupied (0)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("UPDATE rooms SET is_available=? WHERE room_id=?", (available, room_id))
        conn.commit()
        conn.close()

    # ---------- RESERVATION FUNCTIONS ----------
    def add_reservation(self, guest_id, room_id, check_in, check_out, total, status):
        """Add a reservation to the DB."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reservations (guest_id, room_id, check_in_date, check_out_date, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (guest_id, room_id, check_in, check_out, total, status))
        conn.commit()
        conn.close()

    def get_all_reservations(self):
        """Return all reservation info with guest and room details."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.reservation_id,
                   g.first_name || ' ' || g.last_name AS guest_name,
                   rm.room_number,
                   r.check_in_date, r.check_out_date,
                   r.total_price, r.status
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def update_reservation(self, reservation_id, new_status):
        """Update reservation status, like cancelling or confirming."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("UPDATE reservations SET status=? WHERE reservation_id=?", (new_status, reservation_id))
        conn.commit()
        conn.close()

    def delete_reservation(self, reservation_id):
        """Remove a reservation entirely."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM reservations WHERE reservation_id=?", (reservation_id,))
        conn.commit()
        conn.close()

