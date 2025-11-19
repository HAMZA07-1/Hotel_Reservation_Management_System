import sqlite3
import os


class DatabaseManager:
    """Handles all database operations for rooms, guests, and reservations."""

    OCCUPIED_STATUSES = ("Confirmed", "Checked-in", "Checked-out")

    def __init__(self, db_name="hotel.db"):
        self.db_name = db_name
        self.create_if_missing()

    # ---------------------------------------------------
    # Database Setup
    # ---------------------------------------------------
    def create_tables(self):
        """Create minimal tables (for setup or testing)."""
        conn = self.connect()
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number INTEGER,
                room_type TEXT,
                smoking INTEGER DEFAULT 0,
                capacity INTEGER,
                price REAL,
                is_available INTEGER
            );

            CREATE TABLE IF NOT EXISTS guests (
                guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT
            );

            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER,
                room_id INTEGER,
                check_in_date TEXT,
                check_out_date TEXT,
                total_price REAL,
                status TEXT,
                FOREIGN KEY (guest_id) REFERENCES guests (guest_id),
                FOREIGN KEY (room_id) REFERENCES rooms (room_id)
            );
        """)
        conn.commit()
        conn.close()
        print("[Setup] Tables created or verified.")

    def create_if_missing(self):
        """Ensure the database exists with basic tables and initial data."""
        create_script = "database_scripts/001_create_tables.sql"
        populate_script = "database_scripts/002_populate_rooms.sql"

        if os.path.exists(self.db_name):
            print(f"(i) Database '{self.db_name}' already exists. Skipping setup.")
            return

        print("[Setup] Creating new hotel database...")
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        try:
            with open(create_script, "r") as file:
                cur.executescript(file.read())
            with open(populate_script, "r") as file:
                cur.executescript(file.read())
            conn.commit()
            print("[Setup] Database created successfully.")
        except Exception as e:
            print(f"[Error] during DB setup: {e}")
        finally:
            conn.close()

    def connect(self):
        """Return a new database connection."""
        return sqlite3.connect(self.db_name)

    # ---------------------------------------------------
    # Guest Methods
    # ---------------------------------------------------
    def add_guest(self, first_name, last_name, email, phone, address):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO guests (first_name, last_name, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, address))
        conn.commit()
        conn.close()

    def get_guest(self, guest_id=None, email=None):
        if guest_id is None and email is None:
            raise ValueError("Provide guest_id or email to search for guest.")
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if guest_id:
            cur.execute("SELECT * FROM guests WHERE guest_id = ?", (guest_id,))
        else:
            cur.execute("SELECT * FROM guests WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        return row

    def guest_exists(self, guest_id=None, email=None):
        return self.get_guest(guest_id=guest_id, email=email) is not None

    # ---------------------------------------------------
    # Room Methods
    # ---------------------------------------------------
    def add_room(self, room_number, room_type, capacity, price, available):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rooms (room_number, room_type, capacity, price, is_available)
            VALUES (?, ?, ?, ?, ?)
        """, (room_number, room_type, capacity, price, available))
        conn.commit()
        conn.close()

    def get_room(self, room_id=None, room_number=None):
        if room_id is None and room_number is None:
            raise ValueError("Provide room_id or room_number.")
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if room_id:
            cur.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
        else:
            cur.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
        row = cur.fetchone()
        conn.close()
        return row

    # ---------------------------------------------------
    # Reservation Methods
    # ---------------------------------------------------
    def add_reservation(self, guest_id, room_id, check_in_date, check_out_date, total_price, status):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO reservations
                (guest_id, room_id, check_in_date, check_out_date, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (guest_id, room_id, check_in_date, check_out_date, total_price, status))
            conn.commit()
            new_id = cur.lastrowid
            print(f"[Debug] Reservation created with ID {new_id}")
            return new_id
        except Exception as e:
            print(f"[Error] Failed to add reservation: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def cancel_reservation(self, reservation_id: int, guest_id: int) -> bool:
        conn = self.connect()
        cur = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            cur.execute("""
                SELECT status FROM reservations
                WHERE reservation_id = ? AND guest_id = ?
            """, (reservation_id, guest_id))
            row = cur.fetchone()
            if not row or row[0] == "Cancelled":
                return False
            cur.execute("""
                UPDATE reservations
                SET status = 'Cancelled'
                WHERE reservation_id = ? AND guest_id = ?
            """, (reservation_id, guest_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"[Error] Cancel reservation failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_reservation(self, reservation_id, check_in_date, check_out_date, total_price, status):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE reservations
                SET check_in_date = ?,
                    check_out_date = ?,
                    total_price = ?,
                    status = ?
                WHERE reservation_id = ?
            """, (check_in_date, check_out_date, total_price, status, reservation_id))
            if cur.rowcount == 0:
                print(f"[Warn] No reservation found with ID {reservation_id}")
                return False
            conn.commit()
            print(f"[Debug] Reservation {reservation_id} updated successfully.")
            return True
        except Exception as e:
            print(f"[Error] Failed to update reservation {reservation_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def view_reservations(self):
        try:
            conn = self.connect()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            query = """
            SELECT 
                r.reservation_id,
                g.first_name || ' ' || g.last_name AS guest_name,
                r.room_id,
                COALESCE(rm.room_number, r.room_id) AS room_number,
                r.check_in_date,
                r.check_out_date,
                r.total_price,
                r.status
            FROM reservations AS r
            JOIN guests AS g ON r.guest_id = g.guest_id
            LEFT JOIN rooms AS rm ON r.room_id = rm.room_id
            ORDER BY r.reservation_id ASC;
            """

            cur.execute(query)
            rows = cur.fetchall()
            print("[Debug] view_reservations fetched:", len(rows), "rows")
            return rows

        except Exception as e:
            print("[Error view_reservations]:", e)
            return []
        finally:
            conn.close()
